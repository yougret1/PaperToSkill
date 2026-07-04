import json
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")


RANDOM_STATE = 42
TRAIN_PATH = "train.csv"
VALID_PATH = "validation_features.csv"
SUBMISSION_PATH = "submission.csv"


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def normalize_bool_series(s):
    return (
        s.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": "True", "false": "False", "1": "True", "0": "False"})
        .fillna("Missing")
    )


def add_features(train_df, valid_df):
    train_df = train_df.copy()
    valid_df = valid_df.copy()

    train_df["_is_train"] = 1
    valid_df["_is_train"] = 0
    full = pd.concat([train_df, valid_df], axis=0, ignore_index=True)

    passenger = full["PassengerId"].astype(str)
    full["GroupId"] = passenger.str.split("_").str[0]
    full["GroupNum"] = pd.to_numeric(full["GroupId"], errors="coerce")
    group_size = full.groupby("GroupId")["PassengerId"].transform("size")
    full["GroupSize"] = group_size
    full["IsAlone"] = (group_size == 1).astype(int)

    if "Cabin" in full.columns:
        cabin = full["Cabin"].astype("string").fillna("Missing/Missing/Missing").str.split("/", expand=True)
        full["CabinDeck"] = cabin[0].fillna("Missing")
        full["CabinNum"] = pd.to_numeric(cabin[1], errors="coerce")
        full["CabinSide"] = cabin[2].fillna("Missing")
    else:
        full["CabinDeck"] = "Missing"
        full["CabinNum"] = np.nan
        full["CabinSide"] = "Missing"

    spend_cols = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
    for col in spend_cols:
        if col not in full.columns:
            full[col] = 0.0
        full[col] = pd.to_numeric(full[col], errors="coerce")

    full["TotalSpend"] = full[spend_cols].sum(axis=1, skipna=True)
    full["LogTotalSpend"] = np.log1p(full["TotalSpend"])
    full["NoSpend"] = (full["TotalSpend"].fillna(0) == 0).astype(int)
    full["LuxurySpend"] = full[["FoodCourt", "ShoppingMall", "Spa", "VRDeck"]].sum(axis=1, skipna=True)
    full["ServiceSpend"] = full[["RoomService", "Spa", "VRDeck"]].sum(axis=1, skipna=True)

    for col in spend_cols:
        full[f"Log_{col}"] = np.log1p(full[col].clip(lower=0))
        full[f"{col}_Share"] = full[col].fillna(0) / (full["TotalSpend"].fillna(0) + 1.0)

    if "Age" in full.columns:
        full["Age"] = pd.to_numeric(full["Age"], errors="coerce")
        full["AgeBin"] = pd.cut(
            full["Age"],
            bins=[-1, 12, 18, 25, 35, 50, 65, 200],
            labels=["child", "teen", "young", "adult", "mid", "senior", "elder"],
        ).astype("string").fillna("Missing")
    else:
        full["Age"] = np.nan
        full["AgeBin"] = "Missing"

    if "Name" in full.columns:
        surname = full["Name"].astype("string").str.split().str[-1].fillna("Missing")
        full["FamilySize"] = surname.groupby(surname).transform("size")
    else:
        full["FamilySize"] = 1

    for col in ["CryoSleep", "VIP"]:
        if col in full.columns:
            full[col] = normalize_bool_series(full[col])
        else:
            full[col] = "Missing"

    for col in ["HomePlanet", "Destination"]:
        if col not in full.columns:
            full[col] = "Missing"
        full[col] = full[col].astype("string").fillna("Missing")

    full["CryoSleep_NoSpend"] = ((full["CryoSleep"] == "True") & (full["NoSpend"] == 1)).astype(int)
    full["DeckSide"] = full["CabinDeck"].astype(str) + "_" + full["CabinSide"].astype(str)
    full["GroupSizeCat"] = full["GroupSize"].clip(upper=8).astype(str)

    train_out = full[full["_is_train"] == 1].drop(columns=["_is_train"])
    valid_out = full[full["_is_train"] == 0].drop(columns=["_is_train"])
    return train_out, valid_out


def build_model(numeric_features, categorical_features):
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_ohe()),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ],
        remainder="drop",
    )

    estimators = [
        (
            "gb",
            GradientBoostingClassifier(
                n_estimators=220,
                learning_rate=0.035,
                max_depth=3,
                subsample=0.85,
                random_state=RANDOM_STATE,
            ),
        ),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=450,
                max_depth=9,
                min_samples_leaf=3,
                max_features="sqrt",
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=RANDOM_STATE + 1,
            ),
        ),
        (
            "et",
            ExtraTreesClassifier(
                n_estimators=500,
                max_depth=10,
                min_samples_leaf=3,
                max_features="sqrt",
                class_weight="balanced",
                n_jobs=-1,
                random_state=RANDOM_STATE + 2,
            ),
        ),
        (
            "lr",
            LogisticRegression(
                C=0.65,
                max_iter=2000,
                class_weight="balanced",
                solver="lbfgs",
            ),
        ),
    ]

    voter = VotingClassifier(estimators=estimators, voting="soft", weights=[3, 2, 2, 1], n_jobs=-1)
    return Pipeline(steps=[("prep", preprocessor), ("model", voter)])


def main():
    train = pd.read_csv(TRAIN_PATH)
    valid = pd.read_csv(VALID_PATH)

    if os.path.exists("error_or_score_feedback.md"):
        with open("error_or_score_feedback.md", "r", encoding="utf-8", errors="ignore") as f:
            _ = f.read()
    if os.path.exists("baseline_score.json"):
        with open("baseline_score.json", "r", encoding="utf-8", errors="ignore") as f:
            try:
                _ = json.load(f)
            except Exception:
                _ = None

    train_fe, valid_fe = add_features(train, valid)

    y = train_fe["Transported"]
    if y.dtype != bool:
        y = y.astype("string").str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0}).astype(int)
    else:
        y = y.astype(int)

    numeric_features = [
        "Age",
        "RoomService",
        "FoodCourt",
        "ShoppingMall",
        "Spa",
        "VRDeck",
        "GroupNum",
        "GroupSize",
        "IsAlone",
        "CabinNum",
        "TotalSpend",
        "LogTotalSpend",
        "NoSpend",
        "LuxurySpend",
        "ServiceSpend",
        "FamilySize",
        "CryoSleep_NoSpend",
    ]
    spend_cols = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
    numeric_features += [f"Log_{c}" for c in spend_cols] + [f"{c}_Share" for c in spend_cols]

    categorical_features = [
        "HomePlanet",
        "CryoSleep",
        "Destination",
        "VIP",
        "CabinDeck",
        "CabinSide",
        "DeckSide",
        "AgeBin",
        "GroupSizeCat",
    ]

    numeric_features = [c for c in numeric_features if c in train_fe.columns]
    categorical_features = [c for c in categorical_features if c in train_fe.columns]

    X = train_fe[numeric_features + categorical_features]
    X_valid = valid_fe[numeric_features + categorical_features]

    base_model = build_model(numeric_features, categorical_features)

    oof = np.zeros(len(X), dtype=float)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    for train_idx, hold_idx in cv.split(X, y):
        fold_model = clone(base_model)
        fold_model.fit(X.iloc[train_idx], y.iloc[train_idx])
        oof[hold_idx] = fold_model.predict_proba(X.iloc[hold_idx])[:, 1]

    thresholds = np.linspace(0.35, 0.65, 121)
    scores = [accuracy_score(y, oof >= t) for t in thresholds]
    best_threshold = float(thresholds[int(np.argmax(scores))])

    final_model = clone(base_model)
    final_model.fit(X, y)
    valid_proba = final_model.predict_proba(X_valid)[:, 1]
    pred = valid_proba >= best_threshold

    submission = pd.DataFrame(
        {
            "PassengerId": valid["PassengerId"],
            "Transported": pred.astype(bool),
        }
    )
    submission.to_csv(SUBMISSION_PATH, index=False)


if __name__ == "__main__":
    main()
