import os
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "PassengerId" in out.columns:
        pid = out["PassengerId"].astype(str)
        out["Group"] = pid.str.split("_").str[0].astype(float)
        out["GroupMember"] = pid.str.split("_").str[1].astype(float)
        out["GroupSize"] = out.groupby("Group")["PassengerId"].transform("count").astype(float)

    if "Cabin" in out.columns:
        cabin = out["Cabin"].fillna("U/-1/U").astype(str).str.split("/", expand=True)
        out["CabinDeck"] = cabin[0].replace("nan", np.nan)
        out["CabinNum"] = pd.to_numeric(cabin[1], errors="coerce")
        out["CabinSide"] = cabin[2].replace("nan", np.nan)

    spend_cols = [c for c in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"] if c in out.columns]
    if spend_cols:
        out["TotalSpend"] = out[spend_cols].fillna(0).sum(axis=1)
        out["NoSpend"] = (out["TotalSpend"] == 0).astype(int)
        out["LogTotalSpend"] = np.log1p(out["TotalSpend"])
        for col in spend_cols:
            out[f"Log{col}"] = np.log1p(out[col].fillna(0))

    if "Age" in out.columns:
        out["IsChild"] = (out["Age"].fillna(out["Age"].median()) < 13).astype(int)
        out["AgeBin"] = pd.cut(
            out["Age"],
            bins=[-1, 12, 18, 30, 45, 65, 200],
            labels=["child", "teen", "young", "adult", "senior", "elder"],
        ).astype(object)

    for col in ["CryoSleep", "VIP"]:
        if col in out.columns:
            out[col] = out[col].map({True: "True", False: "False"}).fillna("Missing")

    if "Name" in out.columns:
        out = out.drop(columns=["Name"])

    return out


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse=False)


def make_model(X: pd.DataFrame, estimator) -> Pipeline:
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_ohe())]), categorical_cols),
        ],
        remainder="drop",
    )

    return Pipeline([("preprocess", preprocessor), ("model", estimator)])


def make_scaled_logistic(X: pd.DataFrame) -> Pipeline:
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_ohe())]), categorical_cols),
        ],
        remainder="drop",
    )

    return Pipeline(
        [
            ("preprocess", preprocessor),
            ("model", LogisticRegression(C=0.8, max_iter=2000, class_weight="balanced", solver="lbfgs")),
        ]
    )


def main():
    train = pd.read_csv("train.csv")
    validation = pd.read_csv("validation_features.csv")

    target_col = "Transported"
    id_col = "PassengerId"

    y = train[target_col]
    if y.dtype == object:
        y = y.astype(str).str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0}).astype(int)
    else:
        y = y.astype(int)

    combined = pd.concat(
        [train.drop(columns=[target_col]), validation],
        axis=0,
        ignore_index=True,
        sort=False,
    )
    combined_fe = add_features(combined)

    X = combined_fe.iloc[: len(train)].copy()
    X_valid = combined_fe.iloc[len(train) :].copy()

    drop_cols = [id_col]
    X_model = X.drop(columns=[c for c in drop_cols if c in X.columns])
    X_valid_model = X_valid.drop(columns=[c for c in drop_cols if c in X_valid.columns])

    # The weak baseline scored near chance; this uses a small local AIDE-style search over
    # robust tabular models and keeps the best cross-validated branch.
    candidates = [
        (
            "hist_gbdt",
            make_model(
                X_model,
                HistGradientBoostingClassifier(
                    learning_rate=0.045,
                    max_iter=260,
                    max_leaf_nodes=24,
                    l2_regularization=0.08,
                    random_state=42,
                ),
            ),
        ),
        (
            "extra_trees",
            make_model(
                X_model,
                ExtraTreesClassifier(
                    n_estimators=650,
                    max_features="sqrt",
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ),
        (
            "random_forest",
            make_model(
                X_model,
                RandomForestClassifier(
                    n_estimators=500,
                    max_depth=12,
                    min_samples_leaf=3,
                    max_features="sqrt",
                    class_weight="balanced_subsample",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ),
        ("logistic", make_scaled_logistic(X_model)),
    ]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scored = []
    for name, model in candidates:
        try:
            score = cross_val_score(model, X_model, y, cv=cv, scoring="accuracy", n_jobs=-1).mean()
        except Exception:
            score = -1.0
        scored.append((score, name, model))

    scored.sort(reverse=True, key=lambda item: item[0])
    top = scored[:3]

    estimators = [(name, model) for _, name, model in top]
    ensemble = VotingClassifier(estimators=estimators, voting="soft", weights=[3, 2, 1][: len(estimators)], n_jobs=-1)

    try:
        ensemble_scores = cross_val_score(ensemble, X_model, y, cv=cv, scoring="accuracy", n_jobs=-1)
        best_model = ensemble if ensemble_scores.mean() >= top[0][0] - 0.002 else top[0][2]
    except Exception:
        best_model = top[0][2]

    best_model.fit(X_model, y)
    pred = best_model.predict(X_valid_model).astype(bool)

    submission = pd.DataFrame(
        {
            id_col: validation[id_col],
            target_col: pred,
        }
    )
    submission.to_csv("submission.csv", index=False)


if __name__ == "__main__":
    main()
