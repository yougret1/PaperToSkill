import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

TRAIN_PATH = "train.csv"
VALIDATION_PATH = "validation_features.csv"
OUTPUT_PATH = "submission.csv"
SEED = 42


def normalize_target(series):
    if pd.api.types.is_bool_dtype(series):
        return series.astype(int)
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(int)
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0, "yes": 1, "no": 0})
        .astype(int)
    )


def engineer_features(frame, group_sizes, surname_sizes):
    df = frame.copy()

    passenger_id = df["PassengerId"].fillna("Unknown_0").astype(str)
    id_parts = passenger_id.str.split("_", n=1, expand=True)
    df["GroupId"] = id_parts[0].fillna("Unknown")
    df["GroupMember"] = pd.to_numeric(id_parts[1], errors="coerce")
    df["GroupSize"] = df["GroupId"].map(group_sizes).fillna(1).astype(float)
    df["TravellingAlone"] = (df["GroupSize"] == 1).astype(str)

    cabin = df.get("Cabin", pd.Series(index=df.index, dtype=object))
    cabin_parts = cabin.fillna("Unknown/Unknown/Unknown").astype(str).str.split(
        "/", n=2, expand=True
    )
    df["CabinDeck"] = cabin_parts[0].fillna("Unknown")
    df["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    df["CabinSide"] = cabin_parts[2].fillna("Unknown")
    df["CabinKnown"] = cabin.notna().astype(str)
    df["CabinRegion"] = (df["CabinNumber"] // 100).fillna(-1).astype(int).astype(str)
    df["DeckSide"] = df["CabinDeck"].astype(str) + "_" + df["CabinSide"].astype(str)

    name = df.get("Name", pd.Series(index=df.index, dtype=object))
    df["Surname"] = (
        name.fillna("Unknown").astype(str).str.rsplit(" ", n=1).str[-1]
    )
    df["SurnameSize"] = df["Surname"].map(surname_sizes).fillna(1).astype(float)
    df["FamilyAlone"] = (df["SurnameSize"] == 1).astype(str)

    spend_columns = [
        column
        for column in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
        if column in df.columns
    ]
    for column in spend_columns:
        numeric = pd.to_numeric(df[column], errors="coerce")
        df[column] = numeric
        df[f"Log{column}"] = np.log1p(numeric.clip(lower=0))

    if spend_columns:
        spend = df[spend_columns]
        df["TotalSpend"] = spend.fillna(0).sum(axis=1)
        df["LogTotalSpend"] = np.log1p(df["TotalSpend"])
        df["SpendServices"] = (spend.fillna(0) > 0).sum(axis=1)
        df["NoSpend"] = (df["TotalSpend"] == 0).astype(str)
        df["MissingSpendValues"] = spend.isna().sum(axis=1)

    age = pd.to_numeric(
        df.get("Age", pd.Series(index=df.index, dtype=float)), errors="coerce"
    )
    df["Age"] = age
    df["AgeBand"] = pd.cut(
        age,
        bins=[-np.inf, 5, 12, 18, 25, 40, 60, np.inf],
        labels=["0-5", "6-12", "13-18", "19-25", "26-40", "41-60", "61+"],
    ).astype(object)
    df["IsChild"] = (age < 13).fillna(False).astype(str)

    if "HomePlanet" in df.columns and "Destination" in df.columns:
        df["Route"] = (
            df["HomePlanet"].fillna("Unknown").astype(str)
            + "_"
            + df["Destination"].fillna("Unknown").astype(str)
        )

    if "CryoSleep" in df.columns:
        cryo = df["CryoSleep"].map(
            {True: "True", False: "False", "True": "True", "False": "False"}
        )
        df["CryoSleep"] = cryo.fillna("Unknown")
        if "NoSpend" in df.columns:
            df["CryoSpendState"] = df["CryoSleep"] + "_" + df["NoSpend"]

    if "VIP" in df.columns:
        df["VIP"] = (
            df["VIP"]
            .map({True: "True", False: "False", "True": "True", "False": "False"})
            .fillna("Unknown")
        )

    df["MissingValues"] = frame.isna().sum(axis=1)
    df = df.drop(columns=["PassengerId", "Name", "Cabin"], errors="ignore")
    return df


def add_target_history(train_x, valid_x, target, column, prefix, min_train_peers=1):
    global_mean = float(target.mean())
    stats = (
        pd.DataFrame({column: train_x[column].astype(str), "_target": target.values})
        .groupby(column)["_target"]
        .agg(["sum", "count"])
    )

    train_keys = train_x[column].astype(str)
    train_sum = train_keys.map(stats["sum"]).astype(float) - target.to_numpy()
    train_count = train_keys.map(stats["count"]).astype(float) - 1
    train_rate = np.where(
        train_count >= min_train_peers,
        (train_sum + 5.0 * global_mean) / (train_count + 5.0),
        global_mean,
    )

    valid_keys = valid_x[column].astype(str)
    valid_sum = valid_keys.map(stats["sum"]).fillna(0).astype(float)
    valid_count = valid_keys.map(stats["count"]).fillna(0).astype(float)
    valid_rate = np.where(
        valid_count >= 1,
        (valid_sum + 5.0 * global_mean) / (valid_count + 5.0),
        global_mean,
    )

    train_x[f"{prefix}TargetRate"] = train_rate
    valid_x[f"{prefix}TargetRate"] = valid_rate
    train_x[f"{prefix}KnownPeers"] = train_count.clip(lower=0)
    valid_x[f"{prefix}KnownPeers"] = valid_count


train = pd.read_csv(TRAIN_PATH)
validation = pd.read_csv(VALIDATION_PATH)

target = normalize_target(train.pop("Transported"))
validation_ids = validation["PassengerId"].copy()

combined = pd.concat([train, validation], axis=0, ignore_index=True)
combined_passenger_ids = combined["PassengerId"].fillna("Unknown_0").astype(str)
combined_group_ids = combined_passenger_ids.str.split("_", n=1).str[0]
group_sizes = combined_group_ids.value_counts()

combined_names = combined.get(
    "Name", pd.Series("Unknown", index=combined.index, dtype=object)
)
combined_surnames = (
    combined_names.fillna("Unknown").astype(str).str.rsplit(" ", n=1).str[-1]
)
surname_sizes = combined_surnames.value_counts()

train_x = engineer_features(train, group_sizes, surname_sizes)
valid_x = engineer_features(validation, group_sizes, surname_sizes)

add_target_history(train_x, valid_x, target, "GroupId", "Group", min_train_peers=1)
add_target_history(train_x, valid_x, target, "Surname", "Family", min_train_peers=2)

categorical_columns = train_x.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

for column in categorical_columns:
    train_x[column] = train_x[column].astype(object).where(
        train_x[column].notna(), "Unknown"
    ).astype(str)
    valid_x[column] = valid_x[column].astype(object).where(
        valid_x[column].notna(), "Unknown"
    ).astype(str)

numeric_columns = [c for c in train_x.columns if c not in categorical_columns]
for column in numeric_columns:
    train_x[column] = pd.to_numeric(train_x[column], errors="coerce")
    valid_x[column] = pd.to_numeric(valid_x[column], errors="coerce")
    median = train_x[column].median()
    if pd.isna(median):
        median = 0.0
    train_x[column] = train_x[column].replace([np.inf, -np.inf], np.nan).fillna(median)
    valid_x[column] = valid_x[column].replace([np.inf, -np.inf], np.nan).fillna(median)

try:
    from catboost import CatBoostClassifier

    prediction_probabilities = []
    for seed in (SEED, SEED + 17):
        model = CatBoostClassifier(
            iterations=850,
            depth=7,
            learning_rate=0.04,
            loss_function="Logloss",
            eval_metric="Accuracy",
            l2_leaf_reg=6.0,
            random_seed=seed,
            random_strength=0.7,
            bootstrap_type="Bayesian",
            bagging_temperature=0.6,
            verbose=False,
            allow_writing_files=False,
            thread_count=-1,
        )
        model.fit(train_x, target, cat_features=categorical_columns)
        prediction_probabilities.append(model.predict_proba(valid_x)[:, 1])
    probabilities = np.mean(prediction_probabilities, axis=0)
except ImportError:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

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
                            ),
                        ),
                    ]
                ),
                categorical_columns,
            ),
            (
                "numeric",
                SimpleImputer(strategy="median"),
                numeric_columns,
            ),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                HistGradientBoostingClassifier(
                    learning_rate=0.055,
                    max_iter=400,
                    max_leaf_nodes=31,
                    min_samples_leaf=18,
                    l2_regularization=2.0,
                    random_state=SEED,
                ),
            ),
        ]
    )
    model.fit(train_x, target)
    probabilities = model.predict_proba(valid_x)[:, 1]

submission = pd.DataFrame(
    {
        "PassengerId": validation_ids,
        "Transported": probabilities >= 0.5,
    }
)
submission.to_csv(OUTPUT_PATH, index=False)
