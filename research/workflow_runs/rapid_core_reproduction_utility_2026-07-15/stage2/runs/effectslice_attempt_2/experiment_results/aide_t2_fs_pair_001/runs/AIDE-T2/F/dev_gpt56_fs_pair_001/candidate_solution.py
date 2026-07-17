from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
TRAIN_PATH = ROOT / "train.csv"
VALIDATION_PATH = ROOT / "validation_features.csv"
OUTPUT_PATH = ROOT / "submission.csv"
TARGET = "Transported"
ID_COLUMN = "PassengerId"


def engineer_features(train: pd.DataFrame, validation: pd.DataFrame):
    train = train.copy()
    validation = validation.copy()
    train["_is_train"] = 1
    validation["_is_train"] = 0

    combined = pd.concat([train, validation], ignore_index=True, sort=False)

    passenger_parts = combined[ID_COLUMN].astype("string").str.split("_", n=1, expand=True)
    combined["PassengerGroup"] = passenger_parts[0]
    combined["PassengerNumberInGroup"] = pd.to_numeric(
        passenger_parts[1], errors="coerce"
    )
    combined["PassengerGroupSize"] = combined.groupby("PassengerGroup")[
        ID_COLUMN
    ].transform("size")
    combined["IsAlone"] = (combined["PassengerGroupSize"] == 1).astype(int)

    if "Cabin" in combined:
        cabin_parts = combined["Cabin"].astype("string").str.split("/", expand=True)
        combined["CabinDeck"] = cabin_parts[0]
        combined["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
        combined["CabinSide"] = cabin_parts[2]
        combined["CabinNumberBand"] = (combined["CabinNumber"] // 100).astype("Int64")
        combined["CabinGroupSize"] = combined.groupby("Cabin", dropna=False)[
            ID_COLUMN
        ].transform("size")

    if "Name" in combined:
        combined["Surname"] = (
            combined["Name"].astype("string").str.rsplit(" ", n=1).str[-1]
        )
        combined["SurnameSize"] = combined.groupby("Surname", dropna=False)[
            ID_COLUMN
        ].transform("size")
        combined["NameLength"] = combined["Name"].astype("string").str.len()

    spending_columns = [
        column
        for column in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
        if column in combined
    ]
    if spending_columns:
        spending = combined[spending_columns].apply(pd.to_numeric, errors="coerce")
        combined["TotalSpend"] = spending.fillna(0).sum(axis=1)
        combined["SpendServicesUsed"] = spending.fillna(0).gt(0).sum(axis=1)
        combined["NoSpend"] = combined["TotalSpend"].eq(0).astype(int)
        combined["MaxSpend"] = spending.fillna(0).max(axis=1)
        combined["MeanSpend"] = spending.mean(axis=1)
        combined["LogTotalSpend"] = np.log1p(combined["TotalSpend"])

    if "Age" in combined:
        age = pd.to_numeric(combined["Age"], errors="coerce")
        combined["AgeBand"] = pd.cut(
            age,
            bins=[-np.inf, 12, 18, 25, 40, 60, np.inf],
            labels=["child", "teen", "young_adult", "adult", "older_adult", "senior"],
        )
        combined["IsChild"] = age.lt(13).astype(int)

    if "CryoSleep" in combined and "TotalSpend" in combined:
        cryo = combined["CryoSleep"].astype("string").str.lower()
        combined["CryoSpendConflict"] = (
            cryo.eq("true") & combined["TotalSpend"].gt(0)
        ).astype(int)

    # Raw names and cabin strings are high-cardinality duplicates of the extracted features.
    combined = combined.drop(columns=["Name", "Cabin"], errors="ignore")

    train_out = combined.loc[combined["_is_train"].eq(1)].drop(
        columns=["_is_train"], errors="ignore"
    )
    validation_out = combined.loc[combined["_is_train"].eq(0)].drop(
        columns=["_is_train", TARGET], errors="ignore"
    )
    return train_out.reset_index(drop=True), validation_out.reset_index(drop=True)


def fit_predict_catboost(x_train, y_train, x_validation):
    from catboost import CatBoostClassifier

    categorical = [
        column
        for column in x_train.columns
        if (
            isinstance(x_train[column].dtype, pd.CategoricalDtype)
            or pd.api.types.is_object_dtype(x_train[column])
            or pd.api.types.is_string_dtype(x_train[column])
            or pd.api.types.is_bool_dtype(x_train[column])
        )
    ]

    x_train = x_train.copy()
    x_validation = x_validation.copy()
    for column in categorical:
        x_train[column] = x_train[column].astype("string").fillna("__MISSING__")
        x_validation[column] = (
            x_validation[column].astype("string").fillna("__MISSING__")
        )

    model = CatBoostClassifier(
        iterations=700,
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
    model.fit(x_train, y_train, cat_features=categorical)
    return model.predict_proba(x_validation)[:, 1]


def fit_predict_sklearn(x_train, y_train, x_validation):
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

    categorical = [
        column
        for column in x_train.columns
        if (
            isinstance(x_train[column].dtype, pd.CategoricalDtype)
            or pd.api.types.is_object_dtype(x_train[column])
            or pd.api.types.is_string_dtype(x_train[column])
            or pd.api.types.is_bool_dtype(x_train[column])
        )
    ]
    numeric = [column for column in x_train.columns if column not in categorical]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                SimpleImputer(strategy="median", add_indicator=True),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        (
                            "imputer",
                            SimpleImputer(
                                strategy="most_frequent",
                                add_indicator=True,
                            ),
                        ),
                        (
                            "encoder",
                            OrdinalEncoder(
                                handle_unknown="use_encoded_value",
                                unknown_value=-1,
                            ),
                        ),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
    )

    extra_trees = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                ExtraTreesClassifier(
                    n_estimators=650,
                    min_samples_leaf=2,
                    max_features=0.8,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    extra_trees.fit(x_train, y_train)
    extra_probabilities = extra_trees.predict_proba(x_validation)[:, 1]

    hist_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                HistGradientBoostingClassifier(
                    learning_rate=0.06,
                    max_iter=350,
                    max_leaf_nodes=31,
                    min_samples_leaf=20,
                    l2_regularization=2.0,
                    random_state=42,
                ),
            ),
        ]
    )
    hist_model.fit(x_train, y_train)
    hist_probabilities = hist_model.predict_proba(x_validation)[:, 1]

    return 0.45 * extra_probabilities + 0.55 * hist_probabilities


def main():
    train = pd.read_csv(TRAIN_PATH)
    validation = pd.read_csv(VALIDATION_PATH)

    if TARGET not in train.columns:
        raise ValueError(f"{TRAIN_PATH.name} must contain {TARGET}")
    if ID_COLUMN not in train.columns or ID_COLUMN not in validation.columns:
        raise ValueError(f"Both input files must contain {ID_COLUMN}")

    validation_ids = validation[ID_COLUMN].copy()
    train, validation = engineer_features(train, validation)

    y_train = train.pop(TARGET)
    if pd.api.types.is_bool_dtype(y_train):
        y_train = y_train.astype(int)
    else:
        normalized = y_train.astype("string").str.strip().str.lower()
        y_train = normalized.map({"true": 1, "false": 0, "1": 1, "0": 0})
        if y_train.isna().any():
            raise ValueError(f"Unsupported values found in {TARGET}")

    x_train = train.drop(columns=[ID_COLUMN], errors="ignore")
    x_validation = validation.drop(columns=[ID_COLUMN], errors="ignore")

    try:
        probabilities = fit_predict_catboost(x_train, y_train, x_validation)
    except (ImportError, ModuleNotFoundError):
        probabilities = fit_predict_sklearn(x_train, y_train, x_validation)

    submission = pd.DataFrame(
        {
            ID_COLUMN: validation_ids,
            TARGET: np.asarray(probabilities) >= 0.5,
        }
    )
    submission.to_csv(OUTPUT_PATH, index=False)


if __name__ == "__main__":
    main()
