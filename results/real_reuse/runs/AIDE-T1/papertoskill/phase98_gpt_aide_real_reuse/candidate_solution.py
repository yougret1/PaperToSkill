#!/usr/bin/env python3
import json
import os
import re
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42
TRAIN_PATH = "train.csv"
VALID_PATH = "validation_features.csv"
OUT_PATH = "submission.csv"


def bool_to_float(s):
    if s.dtype == bool:
        return s.astype(float)
    return s.map({True: 1.0, False: 0.0, "True": 1.0, "False": 0.0, "true": 1.0, "false": 0.0})


def split_cabin(value, part):
    if pd.isna(value):
        return np.nan
    pieces = str(value).split("/")
    if len(pieces) != 3:
        return np.nan
    if part == 0:
        return pieces[0]
    if part == 1:
        try:
            return float(pieces[1])
        except ValueError:
            return np.nan
    return pieces[2]


def passenger_group(pid):
    if pd.isna(pid):
        return np.nan
    m = re.match(r"^(\d+)_", str(pid))
    return m.group(1) if m else np.nan


def passenger_number(pid):
    if pd.isna(pid):
        return np.nan
    m = re.match(r"^\d+_(\d+)$", str(pid))
    return float(m.group(1)) if m else np.nan


def surname(name):
    if pd.isna(name):
        return np.nan
    parts = str(name).strip().split()
    return parts[-1] if parts else np.nan


def add_features(df):
    df = df.copy()

    spend_cols = [c for c in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"] if c in df.columns]
    for c in spend_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "Cabin" in df.columns:
        df["CabinDeck"] = df["Cabin"].apply(lambda x: split_cabin(x, 0))
        df["CabinNum"] = df["Cabin"].apply(lambda x: split_cabin(x, 1))
        df["CabinSide"] = df["Cabin"].apply(lambda x: split_cabin(x, 2))

    if "PassengerId" in df.columns:
        df["GroupId"] = df["PassengerId"].apply(passenger_group)
        df["PassengerNo"] = df["PassengerId"].apply(passenger_number)
        group_sizes = df.groupby("GroupId")["PassengerId"].transform("size")
        df["GroupSize"] = group_sizes.where(df["GroupId"].notna(), np.nan).astype(float)
        df["IsAlone"] = (df["GroupSize"] == 1).astype(float)

    if "Name" in df.columns:
        df["Surname"] = df["Name"].apply(surname)

    if spend_cols:
        df["TotalSpend"] = df[spend_cols].sum(axis=1, skipna=True)
        df["AnySpend"] = (df["TotalSpend"] > 0).astype(float)
        df["SpendMissingCount"] = df[spend_cols].isna().sum(axis=1).astype(float)
        df["LogTotalSpend"] = np.log1p(df["TotalSpend"].fillna(0))
        for c in spend_cols:
            df[f"Log{c}"] = np.log1p(df[c].fillna(0))

    if "Age" in df.columns:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
        df["IsChild"] = (df["Age"] < 13).astype(float)
        df["AgeBin"] = pd.cut(
            df["Age"],
            bins=[-1, 12, 17, 25, 40, 60, 120],
            labels=["child", "teen", "young_adult", "adult", "older", "senior"],
        ).astype(object)

    for c in ["CryoSleep", "VIP"]:
        if c in df.columns:
            mapped = bool_to_float(df[c])
            if mapped.notna().any():
                df[f"{c}Num"] = mapped

    return df


def make_preprocessor(X):
    drop_cols = [c for c in ["PassengerId", "Name", "Cabin"] if c in X.columns]
    X_model = X.drop(columns=drop_cols, errors="ignore")

    numeric_cols = X_model.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_cols = [c for c in X_model.columns if c not in numeric_cols]

    try:
        encoder = OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", encoder)]), categorical_cols),
        ],
        remainder="drop",
    )
    return preprocessor, drop_cols


def main():
    train = pd.read_csv(TRAIN_PATH)
    valid = pd.read_csv(VALID_PATH)

    if "Transported" not in train.columns:
        raise ValueError("train.csv must contain a Transported target column.")
    if "PassengerId" not in valid.columns:
        raise ValueError("validation_features.csv must contain PassengerId.")

    combined = pd.concat(
        [train.drop(columns=["Transported"]), valid],
        axis=0,
        ignore_index=True,
        sort=False,
    )
    combined_fe = add_features(combined)

    X = combined_fe.iloc[: len(train)].copy()
    X_valid = combined_fe.iloc[len(train) :].copy()
    y = train["Transported"].map({True: 1, False: 0, "True": 1, "False": 0, 1: 1, 0: 0}).astype(int)

    preprocessor, drop_cols = make_preprocessor(X)
    X_model = X.drop(columns=drop_cols, errors="ignore")
    X_valid_model = X_valid.drop(columns=drop_cols, errors="ignore")

    candidates = {
        "hgb": Pipeline(
            [
                ("prep", preprocessor),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        learning_rate=0.055,
                        max_iter=450,
                        max_leaf_nodes=31,
                        l2_regularization=0.03,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            [
                ("prep", preprocessor),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=700,
                        max_features="sqrt",
                        min_samples_leaf=2,
                        class_weight="balanced",
                        n_jobs=-1,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("prep", preprocessor),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=600,
                        max_depth=14,
                        min_samples_leaf=2,
                        max_features="sqrt",
                        class_weight="balanced_subsample",
                        n_jobs=-1,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "logreg": Pipeline(
            [
                (
                    "prep",
                    ColumnTransformer(
                        transformers=[
                            (
                                "num",
                                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                                X_model.select_dtypes(include=["number", "bool"]).columns.tolist(),
                            ),
                            (
                                "cat",
                                Pipeline(
                                    [
                                        ("imputer", SimpleImputer(strategy="most_frequent")),
                                        (
                                            "onehot",
                                            OneHotEncoder(handle_unknown="ignore")
                                            if "sparse_output" not in OneHotEncoder.__init__.__code__.co_varnames
                                            else OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                                        ),
                                    ]
                                ),
                                [c for c in X_model.columns if c not in X_model.select_dtypes(include=["number", "bool"]).columns],
                            ),
                        ],
                        remainder="drop",
                    ),
                ),
                ("model", LogisticRegression(max_iter=2000, C=1.2, class_weight="balanced", random_state=RANDOM_STATE)),
            ]
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = {}
    for name, pipe in candidates.items():
        try:
            vals = cross_val_score(pipe, X_model, y, cv=cv, scoring="accuracy", n_jobs=None)
            scores[name] = float(np.mean(vals))
        except Exception:
            scores[name] = -1.0

    ranked = sorted(scores, key=scores.get, reverse=True)
    selected_names = [name for name in ranked[:3] if scores[name] > 0]

    if not selected_names:
        majority = bool(y.mean() >= 0.5)
        submission = pd.DataFrame({"PassengerId": valid["PassengerId"], "Transported": majority})
        submission.to_csv(OUT_PATH, index=False)
        return

    estimators = []
    for name in selected_names:
        estimators.append((name, candidates[name]))

    if len(estimators) >= 2:
        model = VotingClassifier(estimators=estimators, voting="soft", weights=[max(scores[n], 0.001) for n in selected_names])
    else:
        model = estimators[0][1]

    model.fit(X_model, y)

    if hasattr(model, "predict_proba"):
        pred = (model.predict_proba(X_valid_model)[:, 1] >= 0.5).astype(bool)
    else:
        pred = model.predict(X_valid_model).astype(bool)

    submission = pd.DataFrame({"PassengerId": valid["PassengerId"], "Transported": pred})
    submission["Transported"] = submission["Transported"].astype(bool)
    submission.to_csv(OUT_PATH, index=False)

    report = {
        "cv_accuracy_by_candidate": scores,
        "selected_models": selected_names,
        "rows_train": int(len(train)),
        "rows_submission": int(len(submission)),
    }
    with open("model_report.json", "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
