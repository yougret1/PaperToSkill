from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
SPEND_COLUMNS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]


def locate(filename):
    candidates = [Path.cwd() / filename, Path(__file__).resolve().parent / filename]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(filename)


def engineer(train_raw, validation_raw):
    train_rows = len(train_raw)
    combined = pd.concat(
        [train_raw.drop(columns=["Transported"], errors="ignore"), validation_raw],
        ignore_index=True,
        sort=False,
    )

    passenger_parts = combined["PassengerId"].fillna("Unknown_0").astype(str).str.split("_", n=1, expand=True)
    combined["GroupId"] = passenger_parts[0]
    combined["GroupMember"] = pd.to_numeric(passenger_parts[1], errors="coerce")

    cabin_parts = combined["Cabin"].fillna("Unknown/Unknown/Unknown").astype(str).str.split("/", n=2, expand=True)
    combined["CabinDeck"] = cabin_parts[0]
    combined["CabinNumber"] = pd.to_numeric(cabin_parts[1], errors="coerce")
    combined["CabinSide"] = cabin_parts[2]
    combined["CabinKey"] = (
        combined["CabinDeck"].astype(str)
        + "/"
        + cabin_parts[1].astype(str)
        + "/"
        + combined["CabinSide"].astype(str)
    )

    names = combined["Name"].fillna("Unknown Unknown").astype(str)
    combined["Surname"] = names.str.rsplit(n=1).str[-1]
    combined["NameLength"] = names.str.len()

    for column in SPEND_COLUMNS:
        combined[column] = pd.to_numeric(combined[column], errors="coerce")
        combined[f"Log_{column}"] = np.log1p(combined[column].clip(lower=0))

    combined["TotalSpend"] = combined[SPEND_COLUMNS].sum(axis=1, min_count=1)
    combined["AmenityCount"] = combined[SPEND_COLUMNS].gt(0).sum(axis=1)
    combined["NoSpend"] = combined["TotalSpend"].fillna(0).eq(0)
    combined["LuxurySpend"] = combined[["FoodCourt", "Spa", "VRDeck"]].sum(axis=1, min_count=1)
    combined["BasicSpend"] = combined[["RoomService", "ShoppingMall"]].sum(axis=1, min_count=1)
    combined["SpendPerAmenity"] = combined["TotalSpend"] / combined["AmenityCount"].replace(0, np.nan)

    combined["Age"] = pd.to_numeric(combined["Age"], errors="coerce")
    combined["AgeBand"] = pd.cut(
        combined["Age"],
        bins=[-np.inf, 5, 12, 17, 25, 40, 60, np.inf],
        labels=["Infant", "Child", "Teen", "YoungAdult", "Adult", "MiddleAge", "Senior"],
    ).astype(object)
    combined["IsChild"] = combined["Age"].lt(13)
    combined["IsSolo"] = combined["GroupId"].map(combined["GroupId"].value_counts()).eq(1)

    for key, output in [
        ("GroupId", "GroupSize"),
        ("CabinKey", "CabinOccupancy"),
        ("Surname", "SurnameCount"),
    ]:
        combined[output] = combined[key].map(combined[key].value_counts(dropna=False))

    group_spend = combined.groupby("GroupId", dropna=False)["TotalSpend"].transform("mean")
    combined["GroupMeanSpend"] = group_spend
    combined["SpendVsGroup"] = combined["TotalSpend"] - group_spend
    combined["Route"] = (
        combined["HomePlanet"].fillna("Unknown").astype(str)
        + "_"
        + combined["Destination"].fillna("Unknown").astype(str)
    )

    # Raw identifiers are replaced by components that generalize across passengers.
    combined = combined.drop(columns=["PassengerId", "Name", "Cabin"], errors="ignore")
    return combined.iloc[:train_rows].copy(), combined.iloc[train_rows:].copy()


def add_target_encodings(train, validation, target):
    global_mean = float(target.mean())
    for key in ["GroupId", "CabinKey", "Surname"]:
        train_key = train[key].fillna("__MISSING__").astype(str)
        validation_key = validation[key].fillna("__MISSING__").astype(str)

        stats = pd.DataFrame({"key": train_key, "target": target.to_numpy()}).groupby("key")[
            "target"
        ].agg(["sum", "count"])

        sums = train_key.map(stats["sum"]).astype(float)
        counts = train_key.map(stats["count"]).astype(float)
        other_count = counts - 1.0
        train[f"{key}TargetRate"] = np.where(
            other_count > 0,
            (sums - target.to_numpy() + global_mean) / (other_count + 1.0),
            global_mean,
        )

        validation_sums = validation_key.map(stats["sum"])
        validation_counts = validation_key.map(stats["count"])
        validation[f"{key}TargetRate"] = (
            validation_sums.fillna(0.0) + global_mean
        ) / (validation_counts.fillna(0.0) + 1.0)

    return train, validation


def prepare_categories(train, validation):
    categorical = []
    for column in train.columns:
        if (
            train[column].dtype == object
            or isinstance(train[column].dtype, pd.CategoricalDtype)
            or pd.api.types.is_bool_dtype(train[column])
        ):
            categorical.append(column)
            train[column] = train[column].astype(object).where(train[column].notna(), "__MISSING__").astype(str)
            validation[column] = (
                validation[column].astype(object).where(validation[column].notna(), "__MISSING__").astype(str)
            )
        else:
            train[column] = pd.to_numeric(train[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
            validation[column] = (
                pd.to_numeric(validation[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
            )
    return categorical


def predict_with_catboost(train, target, validation, categorical):
    from catboost import CatBoostClassifier

    model = CatBoostClassifier(
        iterations=800,
        depth=7,
        learning_rate=0.045,
        loss_function="Logloss",
        eval_metric="Accuracy",
        l2_leaf_reg=6.0,
        random_seed=SEED,
        random_strength=0.5,
        bagging_temperature=0.5,
        auto_class_weights=None,
        verbose=False,
        allow_writing_files=False,
        thread_count=-1,
    )
    model.fit(train, target, cat_features=categorical)
    return model.predict_proba(validation)[:, 1]


def predict_with_sklearn(train, target, validation, categorical):
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

    numeric = [column for column in train.columns if column not in categorical]
    transformer = ColumnTransformer(
        [
            (
                "categorical",
                Pipeline(
                    [
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
                categorical,
            ),
            (
                "numeric",
                SimpleImputer(strategy="median", add_indicator=True),
                numeric,
            ),
        ],
        sparse_threshold=0,
    )

    train_matrix = transformer.fit_transform(train)
    validation_matrix = transformer.transform(validation)

    hist = HistGradientBoostingClassifier(
        learning_rate=0.055,
        max_iter=400,
        max_leaf_nodes=31,
        min_samples_leaf=18,
        l2_regularization=3.0,
        random_state=SEED,
    )
    extra = ExtraTreesClassifier(
        n_estimators=500,
        min_samples_leaf=2,
        max_features=0.8,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    hist.fit(train_matrix, target)
    extra.fit(train_matrix, target)
    return 0.7 * hist.predict_proba(validation_matrix)[:, 1] + 0.3 * extra.predict_proba(
        validation_matrix
    )[:, 1]


def main():
    train_raw = pd.read_csv(locate("train.csv"))
    validation_raw = pd.read_csv(locate("validation_features.csv"))

    if "Transported" not in train_raw or "PassengerId" not in validation_raw:
        raise ValueError("Expected Transported in train.csv and PassengerId in validation_features.csv")

    passenger_ids = validation_raw["PassengerId"].copy()
    target = (
        train_raw["Transported"]
        .replace({"True": True, "False": False, "1": True, "0": False})
        .astype(bool)
        .astype(int)
    )

    train, validation = engineer(train_raw, validation_raw)
    train, validation = add_target_encodings(train, validation, target)
    categorical = prepare_categories(train, validation)

    try:
        probabilities = predict_with_catboost(train, target, validation, categorical)
    except ImportError:
        probabilities = predict_with_sklearn(train, target, validation, categorical)

    submission = pd.DataFrame(
        {
            "PassengerId": passenger_ids,
            "Transported": probabilities >= 0.5,
        }
    )
    submission.to_csv(Path.cwd() / "submission.csv", index=False)


if __name__ == "__main__":
    main()
