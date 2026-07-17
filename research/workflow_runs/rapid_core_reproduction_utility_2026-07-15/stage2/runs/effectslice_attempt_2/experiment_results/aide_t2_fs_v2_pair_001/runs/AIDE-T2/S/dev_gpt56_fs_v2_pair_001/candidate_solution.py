from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
TRAIN_PATH = BASE_DIR / "train.csv"
VALID_PATH = BASE_DIR / "validation_features.csv"
OUTPUT_PATH = BASE_DIR / "submission.csv"

train = pd.read_csv(TRAIN_PATH)
validation = pd.read_csv(VALID_PATH)

target = train["Transported"].map(
    lambda value: value
    if isinstance(value, (bool, np.bool_))
    else str(value).strip().lower() in {"true", "1", "yes"}
).astype(int)

train_features = train.drop(columns=["Transported"])
all_features = pd.concat(
    [train_features, validation],
    axis=0,
    ignore_index=True,
    sort=False,
)


def engineer(frame):
    result = frame.copy()

    passenger_parts = result["PassengerId"].fillna("Unknown_0").astype(str).str.split("_")
    result["GroupId"] = passenger_parts.str[0]
    result["GroupMember"] = pd.to_numeric(passenger_parts.str[1], errors="coerce")

    cabin_parts = result["Cabin"].fillna("Unknown/-1/Unknown").astype(str).str.split("/")
    result["CabinDeck"] = cabin_parts.str[0]
    result["CabinNumber"] = pd.to_numeric(cabin_parts.str[1], errors="coerce")
    result["CabinSide"] = cabin_parts.str[2]

    result["Surname"] = (
        result["Name"]
        .fillna("Unknown Unknown")
        .astype(str)
        .str.rsplit(n=1)
        .str[-1]
    )
    result["FamilyKey"] = (
        result["Surname"].astype(str)
        + "_"
        + result["HomePlanet"].fillna("Unknown").astype(str)
    )

    spend_columns = [
        column
        for column in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
        if column in result.columns
    ]
    spend = result[spend_columns].apply(pd.to_numeric, errors="coerce")
    result["TotalSpend"] = spend.fillna(0).sum(axis=1)
    result["ServiceCount"] = spend.fillna(0).gt(0).sum(axis=1)
    result["NoSpend"] = result["TotalSpend"].eq(0).astype(int)
    result["LuxurySpend"] = spend.reindex(
        columns=["Spa", "VRDeck"], fill_value=0
    ).fillna(0).sum(axis=1)
    result["EssentialSpend"] = spend.reindex(
        columns=["RoomService", "FoodCourt", "ShoppingMall"], fill_value=0
    ).fillna(0).sum(axis=1)

    age = pd.to_numeric(result["Age"], errors="coerce")
    result["AgeMissing"] = age.isna().astype(int)
    result["IsChild"] = age.lt(13).astype(int)
    result["AgeBand"] = pd.cut(
        age,
        bins=[-np.inf, 12, 17, 25, 35, 50, 65, np.inf],
        labels=["child", "teen", "young", "adult", "middle", "senior", "elder"],
    ).astype("object")

    result["GroupSize"] = result.groupby("GroupId")["GroupId"].transform("size")
    result["FamilySize"] = result.groupby("FamilyKey")["FamilyKey"].transform("size")
    result["CabinGroupSize"] = result.groupby(
        ["CabinDeck", "CabinNumber", "CabinSide"], dropna=False
    )["GroupId"].transform("size")
    result["TravelsAlone"] = result["GroupSize"].eq(1).astype(int)

    result["CabinRegion"] = pd.cut(
        result["CabinNumber"],
        bins=[-np.inf, 299, 599, 899, 1199, 1499, np.inf],
        labels=["r1", "r2", "r3", "r4", "r5", "r6"],
    ).astype("object")

    result = result.drop(columns=["Name", "Cabin", "PassengerId"], errors="ignore")
    return result


engineered = engineer(all_features)
n_train = len(train)
X_train = engineered.iloc[:n_train].copy()
X_validation = engineered.iloc[n_train:].copy()


def add_leave_one_out_signal(train_frame, valid_frame, key, feature_name):
    keys_train = train_frame[key].fillna("Unknown").astype(str)
    keys_valid = valid_frame[key].fillna("Unknown").astype(str)

    stats = pd.DataFrame({"key": keys_train, "target": target}).groupby("key")[
        "target"
    ].agg(["sum", "count"])

    sums = keys_train.map(stats["sum"]).astype(float)
    counts = keys_train.map(stats["count"]).astype(float)
    train_frame[feature_name] = np.where(
        counts > 1,
        (sums - target.to_numpy()) / (counts - 1),
        np.nan,
    )
    train_frame[feature_name + "Known"] = counts.gt(1).astype(int)

    valid_counts = keys_valid.map(stats["count"])
    valid_frame[feature_name] = keys_valid.map(stats["sum"]) / valid_counts
    valid_frame[feature_name + "Known"] = valid_counts.fillna(0).gt(0).astype(int)


add_leave_one_out_signal(X_train, X_validation, "GroupId", "GroupTargetRate")
add_leave_one_out_signal(X_train, X_validation, "FamilyKey", "FamilyTargetRate")

categorical_columns = [
    column
    for column in X_train.columns
    if X_train[column].dtype == "object"
    or isinstance(X_train[column].dtype, pd.CategoricalDtype)
]

for column in categorical_columns:
    X_train[column] = X_train[column].fillna("Unknown").astype(str)
    X_validation[column] = X_validation[column].fillna("Unknown").astype(str)

numeric_columns = [column for column in X_train.columns if column not in categorical_columns]
for column in numeric_columns:
    X_train[column] = pd.to_numeric(X_train[column], errors="coerce")
    X_validation[column] = pd.to_numeric(X_validation[column], errors="coerce")

try:
    from catboost import CatBoostClassifier

    probabilities = np.zeros(len(X_validation), dtype=float)
    for seed in (41, 137, 509):
        model = CatBoostClassifier(
            iterations=900,
            depth=7,
            learning_rate=0.045,
            loss_function="Logloss",
            eval_metric="Accuracy",
            l2_leaf_reg=5.0,
            random_seed=seed,
            random_strength=0.7,
            bootstrap_type="Bayesian",
            bagging_temperature=0.6,
            border_count=128,
            verbose=False,
            allow_writing_files=False,
            thread_count=-1,
        )
        model.fit(X_train, target, cat_features=categorical_columns)
        probabilities += model.predict_proba(X_validation)[:, 1] / 3.0

except ImportError:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

    encoder = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    steps=[
                        (
                            "imputer",
                            SimpleImputer(
                                strategy="constant",
                                fill_value="Unknown",
                            ),
                        ),
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

    X_encoded = encoder.fit_transform(X_train)
    validation_encoded = encoder.transform(X_validation)

    extra_trees = ExtraTreesClassifier(
        n_estimators=700,
        min_samples_leaf=2,
        max_features=0.8,
        class_weight="balanced",
        random_state=137,
        n_jobs=-1,
    )
    histogram_boosting = HistGradientBoostingClassifier(
        learning_rate=0.055,
        max_iter=350,
        max_leaf_nodes=31,
        min_samples_leaf=18,
        l2_regularization=2.0,
        random_state=509,
    )

    extra_trees.fit(X_encoded, target)
    histogram_boosting.fit(X_encoded, target)
    probabilities = (
        0.55 * extra_trees.predict_proba(validation_encoded)[:, 1]
        + 0.45 * histogram_boosting.predict_proba(validation_encoded)[:, 1]
    )

submission = pd.DataFrame(
    {
        "PassengerId": validation["PassengerId"],
        "Transported": probabilities >= 0.5,
    }
)
submission.to_csv(OUTPUT_PATH, index=False)
