from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
TARGET = "Transported"
ID_COLUMN = "PassengerId"

train_path = Path("train.csv")
validation_path = Path("validation_features.csv")

train = pd.read_csv(train_path)
validation = pd.read_csv(validation_path)

if TARGET not in train.columns:
    raise ValueError(f"train.csv must contain the target column {TARGET!r}")
if ID_COLUMN not in train.columns or ID_COLUMN not in validation.columns:
    raise ValueError(f"Both input files must contain {ID_COLUMN!r}")

validation_ids = validation[ID_COLUMN].copy()

target = train[TARGET]
if not pd.api.types.is_bool_dtype(target):
    target = (
        target.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0})
    )
    if target.isna().any():
        raise ValueError("Transported contains unsupported target values")
target = target.astype(int)

train_features = train.drop(columns=[TARGET]).copy()
all_features = pd.concat(
    [train_features, validation],
    axis=0,
    ignore_index=True,
    sort=False,
)

passenger_parts = all_features[ID_COLUMN].astype(str).str.extract(
    r"^(?P<GroupId>[^_]+)(?:_(?P<GroupMember>\d+))?$"
)
all_features["GroupId"] = passenger_parts["GroupId"].fillna(
    all_features[ID_COLUMN].astype(str)
)
all_features["GroupMember"] = pd.to_numeric(
    passenger_parts["GroupMember"], errors="coerce"
)

# Values such as home planet and cabin are frequently shared by travel groups.
for column in ("HomePlanet", "Destination", "Cabin"):
    if column in all_features.columns:
        group_value = all_features.groupby("GroupId", dropna=False)[column].transform(
            lambda values: (
                values.mode(dropna=True).iloc[0]
                if not values.mode(dropna=True).empty
                else np.nan
            )
        )
        all_features[column] = all_features[column].fillna(group_value)

if "Cabin" in all_features.columns:
    cabin = all_features["Cabin"].astype("string").str.extract(
        r"^(?P<CabinDeck>[^/]+)/(?P<CabinNumber>[^/]+)/(?P<CabinSide>[^/]+)$"
    )
    all_features["CabinDeck"] = cabin["CabinDeck"]
    all_features["CabinNumber"] = pd.to_numeric(
        cabin["CabinNumber"], errors="coerce"
    )
    all_features["CabinSide"] = cabin["CabinSide"]
    all_features["CabinKey"] = (
        cabin["CabinDeck"].fillna("Unknown")
        + "/"
        + cabin["CabinNumber"].fillna("Unknown")
        + "/"
        + cabin["CabinSide"].fillna("Unknown")
    )
    all_features["CabinDeckSide"] = (
        cabin["CabinDeck"].fillna("Unknown")
        + "_"
        + cabin["CabinSide"].fillna("Unknown")
    )

if "Name" in all_features.columns:
    all_features["Surname"] = (
        all_features["Name"]
        .astype("string")
        .str.strip()
        .str.split()
        .str[-1]
        .fillna("Unknown")
    )
else:
    all_features["Surname"] = "Unknown"

all_features["GroupSize"] = (
    all_features.groupby("GroupId", dropna=False)["GroupId"].transform("size")
)
all_features["IsSolo"] = (all_features["GroupSize"] == 1).astype(int)
all_features["SurnameSize"] = (
    all_features.groupby("Surname", dropna=False)["Surname"].transform("size")
)

if "CabinKey" in all_features.columns:
    all_features["CabinOccupancy"] = (
        all_features.groupby("CabinKey", dropna=False)["CabinKey"].transform("size")
    )

spend_columns = [
    column
    for column in ("RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck")
    if column in all_features.columns
]
for column in spend_columns:
    all_features[column] = pd.to_numeric(all_features[column], errors="coerce")
    all_features[f"Log{column}"] = np.log1p(all_features[column].clip(lower=0))

if spend_columns:
    all_features["TotalSpend"] = all_features[spend_columns].fillna(0).sum(axis=1)
    all_features["LogTotalSpend"] = np.log1p(all_features["TotalSpend"])
    all_features["NoSpend"] = (all_features["TotalSpend"] == 0).astype(int)
    all_features["NumberOfServices"] = (
        all_features[spend_columns].fillna(0).gt(0).sum(axis=1)
    )

if "Age" in all_features.columns:
    all_features["Age"] = pd.to_numeric(all_features["Age"], errors="coerce")
    all_features["AgeBand"] = pd.cut(
        all_features["Age"],
        bins=[-np.inf, 5, 12, 17, 25, 40, 60, np.inf],
        labels=["Infant", "Child", "Teen", "YoungAdult", "Adult", "Mature", "Senior"],
    )
    all_features["IsChild"] = all_features["Age"].lt(13).astype(int)

n_train = len(train)
engineered_train = all_features.iloc[:n_train].copy()
engineered_validation = all_features.iloc[n_train:].copy()

# Relational target features use leave-one-out values for training rows and only
# labeled training neighbors for validation rows.
for key, feature_name in (
    ("GroupId", "GroupTransportRate"),
    ("Surname", "FamilyTransportRate"),
):
    keys_train = engineered_train[key]
    target_by_key = pd.DataFrame({key: keys_train, "_target": target.to_numpy()})
    aggregates = target_by_key.groupby(key, dropna=False)["_target"].agg(
        ["sum", "count"]
    )

    sums = keys_train.map(aggregates["sum"]).astype(float)
    counts = keys_train.map(aggregates["count"]).astype(float)
    engineered_train[feature_name] = np.where(
        counts > 1,
        (sums - target.to_numpy()) / (counts - 1),
        np.nan,
    )
    engineered_train[f"{feature_name}KnownCount"] = (counts - 1).clip(lower=0)

    validation_counts = engineered_validation[key].map(aggregates["count"])
    engineered_validation[feature_name] = engineered_validation[key].map(
        aggregates["sum"] / aggregates["count"]
    )
    engineered_validation[f"{feature_name}KnownCount"] = validation_counts.fillna(0)

drop_columns = [
    column
    for column in (ID_COLUMN, "Name", "Cabin")
    if column in engineered_train.columns
]
X_train = engineered_train.drop(columns=drop_columns)
X_validation = engineered_validation.drop(columns=drop_columns)

categorical_columns = [
    column
    for column in X_train.columns
    if (
        isinstance(X_train[column].dtype, pd.CategoricalDtype)
        or pd.api.types.is_object_dtype(X_train[column])
        or pd.api.types.is_string_dtype(X_train[column])
        or pd.api.types.is_bool_dtype(X_train[column])
    )
]

for column in categorical_columns:
    X_train[column] = X_train[column].astype("string").fillna("Unknown").astype(str)
    X_validation[column] = (
        X_validation[column].astype("string").fillna("Unknown").astype(str)
    )

for column in X_train.columns:
    if column not in categorical_columns:
        X_train[column] = pd.to_numeric(X_train[column], errors="coerce")
        X_validation[column] = pd.to_numeric(
            X_validation[column], errors="coerce"
        )

try:
    from catboost import CatBoostClassifier

    predictions = np.zeros(len(X_validation), dtype=float)
    for model_seed in (SEED, SEED + 101):
        model = CatBoostClassifier(
            iterations=750,
            depth=7,
            learning_rate=0.04,
            loss_function="Logloss",
            eval_metric="Accuracy",
            l2_leaf_reg=6.0,
            random_seed=model_seed,
            random_strength=0.8,
            bootstrap_type="Bayesian",
            bagging_temperature=0.7,
            allow_writing_files=False,
            verbose=False,
            thread_count=-1,
        )
        model.fit(
            X_train,
            target,
            cat_features=categorical_columns,
        )
        predictions += model.predict_proba(X_validation)[:, 1] / 2.0

except ImportError:
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier

    combined = pd.concat([X_train, X_validation], ignore_index=True, sort=False)
    for column in categorical_columns:
        combined[column] = pd.Categorical(combined[column]).codes.astype(float)

    for column in combined.columns:
        combined[column] = pd.to_numeric(combined[column], errors="coerce")
        median = combined.iloc[:n_train][column].median()
        combined[column] = combined[column].fillna(0.0 if pd.isna(median) else median)

    fallback_train = combined.iloc[:n_train].to_numpy(dtype=float)
    fallback_validation = combined.iloc[n_train:].to_numpy(dtype=float)

    histogram_model = HistGradientBoostingClassifier(
        learning_rate=0.055,
        max_iter=350,
        max_leaf_nodes=31,
        min_samples_leaf=18,
        l2_regularization=2.0,
        random_state=SEED,
    )
    tree_model = ExtraTreesClassifier(
        n_estimators=600,
        min_samples_leaf=2,
        max_features=0.8,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    histogram_model.fit(fallback_train, target)
    tree_model.fit(fallback_train, target)
    predictions = (
        0.6 * histogram_model.predict_proba(fallback_validation)[:, 1]
        + 0.4 * tree_model.predict_proba(fallback_validation)[:, 1]
    )

submission = pd.DataFrame(
    {
        ID_COLUMN: validation_ids,
        TARGET: predictions >= 0.5,
    }
)
submission.to_csv("submission.csv", index=False)
