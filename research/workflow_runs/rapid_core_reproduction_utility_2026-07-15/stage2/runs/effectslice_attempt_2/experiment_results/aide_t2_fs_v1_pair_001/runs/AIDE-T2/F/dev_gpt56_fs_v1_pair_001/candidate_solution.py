from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
train = pd.read_csv(ROOT / "train.csv")
validation = pd.read_csv(ROOT / "validation_features.csv")

feedback_path = ROOT / "error_or_score_feedback.md"
feedback = feedback_path.read_text(encoding="utf-8").lower() if feedback_path.exists() else ""

target_col = "Transported"
if target_col not in train.columns:
    raise ValueError(f"Expected {target_col!r} in train.csv")
if "PassengerId" not in validation.columns:
    raise ValueError("Expected 'PassengerId' in validation_features.csv")

target = (
    train[target_col]
    .replace(
        {
            "True": True,
            "False": False,
            "true": True,
            "false": False,
            "Yes": True,
            "No": False,
            1: True,
            0: False,
        }
    )
    .astype(bool)
)

train_rows = len(train)
all_features = pd.concat(
    [train.drop(columns=[target_col]), validation],
    axis=0,
    ignore_index=True,
    sort=False,
)


def column(name, default=np.nan):
    if name in all_features.columns:
        return all_features[name]
    return pd.Series(default, index=all_features.index)


passenger_id = column("PassengerId").fillna("Unknown_0").astype(str)
id_parts = passenger_id.str.split("_", n=1, expand=True)
all_features["GroupId"] = id_parts[0]
all_features["GroupMember"] = pd.to_numeric(
    id_parts[1] if id_parts.shape[1] > 1 else np.nan, errors="coerce"
)
all_features["GroupSize"] = all_features.groupby("GroupId")["GroupId"].transform("size")
all_features["IsSolo"] = (all_features["GroupSize"] == 1).astype(str)

cabin = column("Cabin").fillna("Unknown/Unknown/Unknown").astype(str)
cabin_parts = cabin.str.split("/", n=2, expand=True)
all_features["CabinDeck"] = cabin_parts[0].replace("", "Unknown")
all_features["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
all_features["CabinSide"] = cabin_parts[2].replace("", "Unknown")
all_features["CabinOccupancy"] = cabin.groupby(cabin).transform("size")
all_features["CabinRegion"] = pd.cut(
    all_features["CabinNumber"],
    bins=[-np.inf, 299, 599, 899, 1199, 1499, 1799, np.inf],
    labels=["0", "1", "2", "3", "4", "5", "6"],
).astype(object)

name = column("Name").fillna("").astype(str)
all_features["Surname"] = name.str.rsplit(n=1).str[-1].replace("", "Unknown")
all_features["FamilySize"] = all_features.groupby("Surname")["Surname"].transform("size")

spend_columns = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
for spend_col in spend_columns:
    all_features[spend_col] = pd.to_numeric(column(spend_col), errors="coerce")

spending = all_features[spend_columns]
all_features["TotalSpend"] = spending.sum(axis=1, min_count=1)
all_features["ServiceSpend"] = spending[["RoomService", "Spa", "VRDeck"]].sum(
    axis=1, min_count=1
)
all_features["LeisureSpend"] = spending[["FoodCourt", "ShoppingMall"]].sum(
    axis=1, min_count=1
)
all_features["SpendVariety"] = spending.fillna(0).gt(0).sum(axis=1)
all_features["NoSpend"] = all_features["TotalSpend"].fillna(0).eq(0).astype(str)

for spend_col in spend_columns + ["TotalSpend", "ServiceSpend", "LeisureSpend"]:
    all_features[f"Log_{spend_col}"] = np.log1p(
        all_features[spend_col].clip(lower=0)
    )

all_features["Age"] = pd.to_numeric(column("Age"), errors="coerce")
all_features["AgeBand"] = pd.cut(
    all_features["Age"],
    bins=[-np.inf, 12, 17, 25, 39, 59, np.inf],
    labels=["child", "teen", "young", "adult", "middle", "senior"],
).astype(object)
all_features["SpendPerPerson"] = all_features["TotalSpend"] / all_features[
    "GroupSize"
].clip(lower=1)

categorical_columns = [
    name
    for name in [
        "HomePlanet",
        "CryoSleep",
        "Destination",
        "VIP",
        "CabinDeck",
        "CabinSide",
        "CabinRegion",
        "AgeBand",
        "NoSpend",
        "IsSolo",
    ]
    if name in all_features.columns
]

drop_columns = [
    name
    for name in ["PassengerId", "Name", "Cabin", "GroupId", "Surname"]
    if name in all_features.columns
]
model_features = all_features.drop(columns=drop_columns)

for name in categorical_columns:
    model_features[name] = model_features[name].fillna("Unknown").astype(str)

numeric_columns = [
    name for name in model_features.columns if name not in categorical_columns
]
for name in numeric_columns:
    model_features[name] = pd.to_numeric(model_features[name], errors="coerce")

try:
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
except TypeError:
    encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

preprocessor = ColumnTransformer(
    [
        (
            "numeric",
            SimpleImputer(strategy="median", add_indicator=True),
            numeric_columns,
        ),
        (
            "categorical",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", encoder),
                ]
            ),
            categorical_columns,
        ),
    ],
    remainder="drop",
)

X_all = preprocessor.fit_transform(model_features)
X_train = X_all[:train_rows]
X_validation = X_all[train_rows:]

min_leaf = 28 if "overfit" in feedback or "overfit" in feedback.replace("-", "") else 18
max_iterations = 300 if "runtime" in feedback or "time limit" in feedback else 450

gradient_model = HistGradientBoostingClassifier(
    learning_rate=0.045,
    max_iter=max_iterations,
    max_leaf_nodes=31,
    min_samples_leaf=min_leaf,
    l2_regularization=1.5,
    early_stopping=True,
    validation_fraction=0.15,
    n_iter_no_change=35,
    random_state=42,
)
gradient_model.fit(X_train, target)

tree_model = ExtraTreesClassifier(
    n_estimators=500,
    max_features=0.75,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=-1,
    random_state=43,
)
tree_model.fit(X_train, target)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_validation_scaled = scaler.transform(X_validation)
linear_model = LogisticRegression(
    C=0.7,
    max_iter=2500,
    class_weight="balanced",
    solver="lbfgs",
    random_state=44,
)
linear_model.fit(X_train_scaled, target)

probabilities = (
    0.55 * gradient_model.predict_proba(X_validation)[:, 1]
    + 0.25 * tree_model.predict_proba(X_validation)[:, 1]
    + 0.20 * linear_model.predict_proba(X_validation_scaled)[:, 1]
)

submission = pd.DataFrame(
    {
        "PassengerId": validation["PassengerId"],
        "Transported": (probabilities >= 0.5).astype(bool),
    }
)
submission.to_csv(ROOT / "submission.csv", index=False)
