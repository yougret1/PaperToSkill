import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


warnings.filterwarnings("ignore")


TRAIN_PATH = Path("train.csv")
VALID_PATH = Path("validation_features.csv")
OUT_PATH = Path("submission.csv")


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=2)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


class FeatureBuilder(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        x = X.copy()
        self.group_size_ = {}
        self.family_size_ = {}

        if "PassengerId" in x.columns:
            groups = x["PassengerId"].astype(str).str.split("_", expand=True)[0]
            self.group_size_ = groups.value_counts().to_dict()

        if "Name" in x.columns:
            families = x["Name"].astype(str).str.split().str[-1].replace("nan", np.nan)
            self.family_size_ = families.value_counts().to_dict()

        return self

    def transform(self, X):
        x = X.copy()

        if "PassengerId" in x.columns:
            pid = x["PassengerId"].astype(str).str.split("_", expand=True)
            x["GroupId"] = pd.to_numeric(pid[0], errors="coerce")
            x["GroupMember"] = pd.to_numeric(pid[1], errors="coerce")
            x["GroupSize"] = pid[0].map(self.group_size_).fillna(1).astype(float)
            x["Solo"] = (x["GroupSize"] == 1).astype(int)

        if "Cabin" in x.columns:
            cabin = x["Cabin"].astype(str).str.split("/", expand=True)
            x["Deck"] = cabin[0].replace("nan", np.nan)
            x["CabinNum"] = pd.to_numeric(cabin[1], errors="coerce")
            x["Side"] = cabin[2].replace("nan", np.nan)
            x["CabinNumBin"] = pd.cut(
                x["CabinNum"],
                bins=[-1, 250, 500, 750, 1000, 1250, 1500, 2000],
                labels=False,
            )

        if "Name" in x.columns:
            x["Family"] = x["Name"].astype(str).str.split().str[-1].replace("nan", np.nan)
            x["FamilySize"] = x["Family"].map(self.family_size_).fillna(1).astype(float)

        spend_cols = [c for c in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"] if c in x.columns]
        if spend_cols:
            spend = x[spend_cols].copy()
            x["TotalSpend"] = spend.sum(axis=1, skipna=True)
            x["AnySpend"] = (x["TotalSpend"] > 0).astype(int)
            x["NoSpend"] = (x["TotalSpend"] == 0).astype(int)
            x["LuxurySpend"] = x[[c for c in ["Spa", "VRDeck"] if c in x.columns]].sum(axis=1, skipna=True)
            x["ServiceSpend"] = x[[c for c in ["RoomService", "FoodCourt", "ShoppingMall"] if c in x.columns]].sum(
                axis=1, skipna=True
            )
            x["SpendMissingCount"] = x[spend_cols].isna().sum(axis=1)

        if "Age" in x.columns:
            x["AgeBin"] = pd.cut(x["Age"], bins=[-1, 12, 18, 25, 35, 50, 65, 120], labels=False)
            x["IsChild"] = (x["Age"] < 13).astype(float)

        for c in ["CryoSleep", "VIP"]:
            if c in x.columns:
                x[c] = x[c].map({True: "True", False: "False", "True": "True", "False": "False"})

        x = x.drop(columns=[c for c in ["PassengerId", "Cabin", "Name"] if c in x.columns], errors="ignore")
        return x


def parse_target(s):
    if s.dtype == bool:
        return s.astype(int).to_numpy()
    return s.astype(str).str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0}).astype(int).to_numpy()


train = pd.read_csv(TRAIN_PATH)
valid = pd.read_csv(VALID_PATH)

passenger_ids = valid["PassengerId"].copy()
y = parse_target(train["Transported"])
X = train.drop(columns=["Transported"])

feature_builder = FeatureBuilder().fit(pd.concat([X, valid], axis=0, ignore_index=True))
X_fe = feature_builder.transform(X)

numeric_cols = X_fe.select_dtypes(include=["number", "bool"]).columns.tolist()
categorical_cols = [c for c in X_fe.columns if c not in numeric_cols]

tree_preprocess = ColumnTransformer(
    transformers=[
        ("num", SimpleImputer(strategy="median"), numeric_cols),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_ohe())]), categorical_cols),
    ],
    remainder="drop",
)

linear_preprocess = ColumnTransformer(
    transformers=[
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_cols),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_ohe())]), categorical_cols),
    ],
    remainder="drop",
)

candidates = [
    (
        "hist_gradient_boosting",
        Pipeline(
            [
                ("features", feature_builder),
                ("prep", tree_preprocess),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        learning_rate=0.055,
                        max_iter=450,
                        max_leaf_nodes=31,
                        l2_regularization=0.05,
                        random_state=42,
                    ),
                ),
            ]
        ),
    ),
    (
        "extra_trees",
        Pipeline(
            [
                ("features", feature_builder),
                ("prep", tree_preprocess),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=700,
                        max_features="sqrt",
                        min_samples_leaf=2,
                        class_weight="balanced_subsample",
                        random_state=43,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    ),
    (
        "random_forest",
        Pipeline(
            [
                ("features", feature_builder),
                ("prep", tree_preprocess),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=650,
                        max_features="sqrt",
                        min_samples_leaf=3,
                        class_weight="balanced_subsample",
                        random_state=44,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    ),
    (
        "logistic_regression",
        Pipeline(
            [
                ("features", feature_builder),
                ("prep", linear_preprocess),
                ("model", LogisticRegression(C=1.2, max_iter=2500, class_weight="balanced", solver="lbfgs")),
            ]
        ),
    ),
]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = []
for name, model in candidates:
    score = float(cross_val_score(model, X, y, cv=cv, scoring="accuracy", n_jobs=None).mean())
    scores.append((score, name, model))

scores.sort(reverse=True, key=lambda t: t[0])
top = scores[:3]

estimators = [(name, model) for _, name, model in top]
weights = [max(score - 0.5, 0.001) for score, _, _ in top]

if len(estimators) >= 2:
    final_model = VotingClassifier(estimators=estimators, voting="soft", weights=weights, n_jobs=None)
else:
    final_model = estimators[0][1]

final_model.fit(X, y)
pred = final_model.predict(valid).astype(bool)

submission = pd.DataFrame({"PassengerId": passenger_ids, "Transported": pred})
submission.to_csv(OUT_PATH, index=False)

with open("model_selection_summary.json", "w") as f:
    json.dump(
        {
            "cv_accuracy": [{"name": name, "accuracy": score} for score, name, _ in scores],
            "selected": [name for _, name, _ in top],
        },
        f,
        indent=2,
    )
