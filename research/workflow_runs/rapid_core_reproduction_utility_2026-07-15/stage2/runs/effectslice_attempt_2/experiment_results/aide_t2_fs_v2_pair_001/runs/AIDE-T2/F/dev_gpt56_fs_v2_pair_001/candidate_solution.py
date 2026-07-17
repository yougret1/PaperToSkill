from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


BASE_DIR = Path(__file__).resolve().parent
TRAIN_PATH = BASE_DIR / "train.csv"
VALIDATION_PATH = BASE_DIR / "validation_features.csv"
OUTPUT_PATH = BASE_DIR / "submission.csv"

SPEND_COLUMNS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]


def to_binary_target(series):
    if pd.api.types.is_bool_dtype(series):
        return series.astype(int)
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(int)
    return series.astype(str).str.strip().str.lower().map(
        {"true": 1, "false": 0, "1": 1, "0": 0}
    ).astype(int)


def add_features(frame, combined_counts):
    result = frame.copy()

    passenger_parts = result["PassengerId"].astype(str).str.split("_", n=1, expand=True)
    result["GroupId"] = passenger_parts[0]
    result["GroupMember"] = pd.to_numeric(passenger_parts[1], errors="coerce")
    result["GroupSize"] = result["GroupId"].map(combined_counts["group"])

    cabin_parts = result["Cabin"].fillna("Unknown/0/Unknown").astype(str).str.split(
        "/", n=2, expand=True
    )
    result["CabinDeck"] = cabin_parts[0]
    result["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    result["CabinSide"] = cabin_parts[2]
    result["CabinRegion"] = pd.cut(
        result["CabinNumber"],
        bins=[-np.inf, 299, 599, 899, 1199, 1499, np.inf],
        labels=["0", "1", "2", "3", "4", "5"],
    ).astype("object")

    names = result["Name"].fillna("Unknown Unknown").astype(str)
    result["Surname"] = names.str.rsplit(n=1).str[-1]
    result["FamilySize"] = result["Surname"].map(combined_counts["surname"])

    available_spend = [column for column in SPEND_COLUMNS if column in result.columns]
    for column in available_spend:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result["TotalSpend"] = result[available_spend].fillna(0).sum(axis=1)
    result["SpendServicesUsed"] = (
        result[available_spend].fillna(0).gt(0).sum(axis=1)
    )
    result["HasSpend"] = result["TotalSpend"].gt(0).astype(int)
    result["LogTotalSpend"] = np.log1p(result["TotalSpend"])
    result["LuxurySpend"] = result[
        [c for c in ["Spa", "VRDeck", "RoomService"] if c in result.columns]
    ].fillna(0).sum(axis=1)
    result["RetailSpend"] = result[
        [c for c in ["FoodCourt", "ShoppingMall"] if c in result.columns]
    ].fillna(0).sum(axis=1)

    age = pd.to_numeric(result["Age"], errors="coerce")
    result["Age"] = age
    result["IsChild"] = age.lt(13).astype(int)
    result["IsYoung"] = age.lt(18).astype(int)
    result["AgeBand"] = pd.cut(
        age,
        bins=[-np.inf, 5, 12, 17, 25, 40, 60, np.inf],
        labels=["infant", "child", "teen", "young_adult", "adult", "middle", "senior"],
    ).astype("object")

    result["CryoNoSpend"] = (
        result["CryoSleep"].astype(str).str.lower().eq("true")
        & result["TotalSpend"].eq(0)
    ).astype(int)
    result["SoloPassenger"] = result["GroupSize"].eq(1).astype(int)

    return result.drop(columns=["Name", "Cabin"], errors="ignore")


def add_group_target_encoding(train_frame, validation_frame, target):
    global_rate = float(target.mean())
    stats = pd.DataFrame(
        {"GroupId": train_frame["GroupId"].astype(str), "target": target.to_numpy()}
    ).groupby("GroupId")["target"].agg(["sum", "count"])

    train_groups = train_frame["GroupId"].astype(str)
    train_sum = train_groups.map(stats["sum"]).astype(float)
    train_count = train_groups.map(stats["count"]).astype(float)

    # Leave each training row's own label out so this feature cannot memorize it.
    other_count = train_count - 1
    train_frame["GroupTargetRate"] = np.where(
        other_count > 0,
        (train_sum - target.to_numpy() + 2.0 * global_rate) / (other_count + 2.0),
        global_rate,
    )
    train_frame["KnownGroupMembers"] = other_count.clip(lower=0)

    validation_groups = validation_frame["GroupId"].astype(str)
    validation_sum = validation_groups.map(stats["sum"])
    validation_count = validation_groups.map(stats["count"])
    validation_frame["GroupTargetRate"] = (
        (validation_sum + 2.0 * global_rate) / (validation_count + 2.0)
    ).fillna(global_rate)
    validation_frame["KnownGroupMembers"] = validation_count.fillna(0)

    return train_frame, validation_frame


def train_catboost(train_features, target, validation_features):
    from catboost import CatBoostClassifier

    categorical_columns = train_features.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    train_cb = train_features.copy()
    validation_cb = validation_features.copy()
    for column in categorical_columns:
        train_cb[column] = train_cb[column].astype("object").fillna("Unknown").astype(str)
        validation_cb[column] = (
            validation_cb[column].astype("object").fillna("Unknown").astype(str)
        )

    model = CatBoostClassifier(
        iterations=850,
        depth=7,
        learning_rate=0.045,
        loss_function="Logloss",
        eval_metric="Accuracy",
        l2_leaf_reg=5.0,
        random_seed=42,
        verbose=False,
        allow_writing_files=False,
        thread_count=-1,
    )
    model.fit(train_cb, target, cat_features=categorical_columns)
    return model.predict_proba(validation_cb)[:, 1]


def train_sklearn(train_features, target, validation_features):
    categorical_columns = train_features.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()
    numeric_columns = [
        column for column in train_features.columns if column not in categorical_columns
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OrdinalEncoder(
                                handle_unknown="use_encoded_value",
                                unknown_value=-1,
                                encoded_missing_value=-1,
                            ),
                        ),
                    ]
                ),
                categorical_columns,
            ),
            (
                "numeric",
                SimpleImputer(strategy="median", add_indicator=True),
                numeric_columns,
            ),
        ],
        verbose_feature_names_out=False,
    )

    ensemble = VotingClassifier(
        estimators=[
            (
                "hist",
                HistGradientBoostingClassifier(
                    learning_rate=0.055,
                    max_iter=350,
                    max_leaf_nodes=25,
                    min_samples_leaf=18,
                    l2_regularization=2.0,
                    random_state=42,
                ),
            ),
            (
                "extra",
                ExtraTreesClassifier(
                    n_estimators=550,
                    max_features=0.8,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    n_jobs=-1,
                    random_state=43,
                ),
            ),
        ],
        voting="soft",
        weights=[3, 2],
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", ensemble),
        ]
    )
    model.fit(train_features, target)
    return model.predict_proba(validation_features)[:, 1]


def main():
    train = pd.read_csv(TRAIN_PATH)
    validation = pd.read_csv(VALIDATION_PATH)

    target_column = "Transported"
    if target_column not in train.columns:
        raise ValueError("train.csv must contain a Transported target column")
    if "PassengerId" not in validation.columns:
        raise ValueError("validation_features.csv must contain PassengerId")

    target = to_binary_target(train.pop(target_column))
    passenger_ids = validation["PassengerId"].copy()

    combined = pd.concat([train, validation], ignore_index=True, sort=False)
    combined_groups = combined["PassengerId"].astype(str).str.split("_", n=1).str[0]
    combined_surnames = (
        combined["Name"]
        .fillna("Unknown Unknown")
        .astype(str)
        .str.rsplit(n=1)
        .str[-1]
    )
    combined_counts = {
        "group": combined_groups.value_counts(),
        "surname": combined_surnames.value_counts(),
    }

    train_features = add_features(train, combined_counts)
    validation_features = add_features(validation, combined_counts)
    train_features, validation_features = add_group_target_encoding(
        train_features, validation_features, target
    )

    validation_features = validation_features.reindex(columns=train_features.columns)

    try:
        probabilities = train_catboost(
            train_features, target, validation_features
        )
    except (ImportError, ModuleNotFoundError):
        probabilities = train_sklearn(
            train_features, target, validation_features
        )

    predictions = probabilities >= 0.5
    submission = pd.DataFrame(
        {
            "PassengerId": passenger_ids,
            "Transported": predictions.astype(bool),
        }
    )
    submission.to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
