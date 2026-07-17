from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
TRAIN_PATH = ROOT / "train.csv"
VALIDATION_PATH = ROOT / "validation_features.csv"
OUTPUT_PATH = ROOT / "submission.csv"


def engineer_features(frame: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()

    passenger = result["PassengerId"].fillna("Unknown_0").astype(str)
    reference_passenger = reference["PassengerId"].fillna("Unknown_0").astype(str)
    result["GroupId"] = passenger.str.split("_").str[0]
    reference_groups = reference_passenger.str.split("_").str[0]
    group_sizes = reference_groups.value_counts()
    result["GroupSize"] = result["GroupId"].map(group_sizes).fillna(1).astype(float)
    result["GroupMember"] = pd.to_numeric(
        passenger.str.split("_").str[-1], errors="coerce"
    )

    if "Cabin" in result:
        cabin = result["Cabin"].fillna("Unknown/Unknown/Unknown").astype(str)
        cabin_parts = cabin.str.split("/", expand=True)
        result["CabinDeck"] = cabin_parts[0]
        result["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
        result["CabinSide"] = cabin_parts[2]
        result["CabinRegion"] = (result["CabinNumber"] // 100).astype("Int64").astype(str)
        result = result.drop(columns=["Cabin"])

    if "Name" in result:
        result["Surname"] = (
            result["Name"].fillna("Unknown").astype(str).str.split().str[-1]
        )
        if "Name" in reference:
            reference_surnames = (
                reference["Name"].fillna("Unknown").astype(str).str.split().str[-1]
            )
            family_sizes = reference_surnames.value_counts()
            result["FamilySize"] = result["Surname"].map(family_sizes).fillna(1)
        result = result.drop(columns=["Name"])

    spending_columns = [
        column
        for column in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
        if column in result
    ]
    if spending_columns:
        spending = result[spending_columns].apply(pd.to_numeric, errors="coerce")
        result["TotalSpend"] = spending.sum(axis=1, min_count=1)
        result["SpendServices"] = spending.notna().mul(spending.fillna(0).gt(0)).sum(axis=1)
        result["NoSpending"] = spending.fillna(0).sum(axis=1).eq(0)
        for column in spending_columns:
            result[f"Log{column}"] = np.log1p(spending[column].clip(lower=0))

    if "Age" in result:
        age = pd.to_numeric(result["Age"], errors="coerce")
        result["Age"] = age
        result["AgeBand"] = pd.cut(
            age,
            bins=[-np.inf, 5, 12, 17, 25, 40, 60, np.inf],
            labels=["Infant", "Child", "Teen", "YoungAdult", "Adult", "MiddleAge", "Senior"],
        ).astype(object)
        result["IsChild"] = age.lt(13)

    return result.drop(columns=["PassengerId"], errors="ignore")


def make_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


train = pd.read_csv(TRAIN_PATH)
validation = pd.read_csv(VALIDATION_PATH)

if "Transported" not in train.columns:
    raise ValueError("train.csv must contain the Transported target column")
if "PassengerId" not in validation.columns:
    raise ValueError("validation_features.csv must contain PassengerId")

target_raw = train.pop("Transported")
if pd.api.types.is_bool_dtype(target_raw) or pd.api.types.is_numeric_dtype(target_raw):
    target = target_raw.astype(int)
else:
    target = (
        target_raw.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0})
    )
    if target.isna().any():
        raise ValueError("Transported must contain boolean or binary values")
    target = target.astype(int)

validation_ids = validation["PassengerId"].copy()
reference = pd.concat([train, validation], ignore_index=True, sort=False)
train_features = engineer_features(train, reference)
validation_features = engineer_features(validation, reference)

categorical_columns = train_features.select_dtypes(
    include=["object", "category", "bool", "string"]
).columns.tolist()
numeric_columns = [
    column for column in train_features.columns if column not in categorical_columns
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            ),
            numeric_columns,
        ),
        (
            "categorical",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot", make_one_hot_encoder()),
                ]
            ),
            categorical_columns,
        ),
    ],
    sparse_threshold=0,
)

train_matrix = preprocessor.fit_transform(train_features)
validation_matrix = preprocessor.transform(validation_features)

boosted_model = HistGradientBoostingClassifier(
    learning_rate=0.055,
    max_iter=350,
    max_leaf_nodes=31,
    min_samples_leaf=18,
    l2_regularization=1.0,
    random_state=42,
)
trees_model = ExtraTreesClassifier(
    n_estimators=500,
    min_samples_leaf=2,
    max_features=0.8,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42,
)

boosted_model.fit(train_matrix, target)
trees_model.fit(train_matrix, target)

probabilities = (
    0.78 * boosted_model.predict_proba(validation_matrix)[:, 1]
    + 0.22 * trees_model.predict_proba(validation_matrix)[:, 1]
)

# Passenger groups often share travel circumstances; use a small within-group
# adjustment while retaining each passenger's individual model prediction.
groups = validation_ids.astype(str).str.split("_").str[0]
group_mean = pd.Series(probabilities).groupby(groups.to_numpy()).transform("mean")
group_size = groups.map(groups.value_counts()).to_numpy()
probabilities = np.where(
    group_size > 1,
    0.88 * probabilities + 0.12 * group_mean.to_numpy(),
    probabilities,
)

submission = pd.DataFrame(
    {
        "PassengerId": validation_ids,
        "Transported": probabilities >= 0.5,
    }
)
submission.to_csv(OUTPUT_PATH, index=False)
