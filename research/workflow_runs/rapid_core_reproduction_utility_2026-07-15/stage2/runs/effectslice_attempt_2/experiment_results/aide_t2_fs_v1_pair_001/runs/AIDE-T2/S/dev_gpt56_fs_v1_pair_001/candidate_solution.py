from pathlib import Path
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
TRAIN_PATH = ROOT / "train.csv"
VALID_PATH = ROOT / "validation_features.csv"
OUTPUT_PATH = ROOT / "submission.csv"

train = pd.read_csv(TRAIN_PATH)
valid = pd.read_csv(VALID_PATH)

target_col = "Transported"
id_col = "PassengerId"

if target_col not in train.columns:
    raise ValueError(f"{TRAIN_PATH.name} must contain {target_col}")
if id_col not in train.columns or id_col not in valid.columns:
    raise ValueError(f"Both input files must contain {id_col}")

y = train[target_col].astype(str).str.lower().map({"true": 1, "false": 0})
if y.isna().any():
    y = pd.to_numeric(train[target_col], errors="raise").astype(int)

all_features = pd.concat(
    [train.drop(columns=[target_col]), valid],
    axis=0,
    ignore_index=True,
)
n_train = len(train)


def engineer(df):
    out = df.copy()

    passenger_parts = out[id_col].fillna("Unknown_0").astype(str).str.split("_")
    out["GroupId"] = passenger_parts.str[0]
    out["GroupMember"] = pd.to_numeric(passenger_parts.str[1], errors="coerce")

    if "Cabin" in out.columns:
        cabin = out["Cabin"].fillna("Unknown/Unknown/Unknown").astype(str).str.split("/")
        out["CabinDeck"] = cabin.str[0]
        out["CabinNumber"] = pd.to_numeric(cabin.str[1], errors="coerce")
        out["CabinSide"] = cabin.str[2]
        out["CabinRegion"] = (out["CabinNumber"] // 100).astype("Int64").astype(str)
        out["DeckSide"] = out["CabinDeck"].astype(str) + "_" + out["CabinSide"].astype(str)

    if "Name" in out.columns:
        names = out["Name"].fillna("Unknown Unknown").astype(str).str.strip()
        out["Surname"] = names.str.split().str[-1]
        out["NameLength"] = names.str.len()

    spend_cols = [
        col for col in ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
        if col in out.columns
    ]
    if spend_cols:
        spend = out[spend_cols].apply(pd.to_numeric, errors="coerce")
        out["TotalSpend"] = spend.fillna(0).sum(axis=1)
        out["AmenitiesUsed"] = spend.fillna(0).gt(0).sum(axis=1)
        out["NoSpend"] = out["TotalSpend"].eq(0).astype(int)
        out["LuxurySpend"] = spend.reindex(
            columns=[c for c in ["Spa", "VRDeck", "RoomService"] if c in spend.columns]
        ).fillna(0).sum(axis=1)

    if "Age" in out.columns:
        age = pd.to_numeric(out["Age"], errors="coerce")
        out["IsChild"] = age.lt(13).astype(int)
        out["AgeBand"] = pd.cut(
            age,
            bins=[-np.inf, 5, 12, 17, 25, 40, 60, np.inf],
            labels=["Baby", "Child", "Teen", "YoungAdult", "Adult", "MiddleAge", "Senior"],
        ).astype(str)

    if "HomePlanet" in out.columns and "Destination" in out.columns:
        out["Route"] = (
            out["HomePlanet"].fillna("Unknown").astype(str)
            + "_"
            + out["Destination"].fillna("Unknown").astype(str)
        )

    group_sizes = out.groupby("GroupId", dropna=False)[id_col].transform("size")
    out["GroupSize"] = group_sizes
    out["TravellingAlone"] = group_sizes.eq(1).astype(int)

    if "Surname" in out.columns:
        out["SurnameSize"] = out.groupby("Surname", dropna=False)[id_col].transform("size")
        out["FamilyGroup"] = out["GroupId"].astype(str) + "_" + out["Surname"].astype(str)

    out = out.drop(columns=[id_col, "Name", "Cabin"], errors="ignore")
    return out


X_all = engineer(all_features)
X_train = X_all.iloc[:n_train].copy()
X_valid = X_all.iloc[n_train:].copy()

# Leave-one-out group evidence avoids using a training row's own label while
# allowing validation passengers to benefit from labeled travelling companions.
global_rate = float(y.mean())
group_key_train = X_train["GroupId"].fillna("Unknown").astype(str)
group_key_valid = X_valid["GroupId"].fillna("Unknown").astype(str)
group_stats = pd.DataFrame({"key": group_key_train, "target": y.to_numpy()}).groupby("key")[
    "target"
].agg(["sum", "count"])

train_group_sum = group_key_train.map(group_stats["sum"]).astype(float) - y.to_numpy()
train_group_count = group_key_train.map(group_stats["count"]).astype(float) - 1.0
valid_group_sum = group_key_valid.map(group_stats["sum"]).fillna(0).astype(float)
valid_group_count = group_key_valid.map(group_stats["count"]).fillna(0).astype(float)

X_train["KnownGroupMembers"] = train_group_count
X_valid["KnownGroupMembers"] = valid_group_count
X_train["KnownGroupRate"] = np.where(
    train_group_count > 0, train_group_sum / train_group_count, global_rate
)
X_valid["KnownGroupRate"] = np.where(
    valid_group_count > 0, valid_group_sum / valid_group_count, global_rate
)

categorical_cols = [
    col
    for col in X_train.columns
    if X_train[col].dtype == "object"
    or isinstance(X_train[col].dtype, pd.CategoricalDtype)
    or str(X_train[col].dtype) == "boolean"
]

for col in categorical_cols:
    X_train[col] = X_train[col].fillna("Missing").astype(str)
    X_valid[col] = X_valid[col].fillna("Missing").astype(str)

numeric_cols = [col for col in X_train.columns if col not in categorical_cols]
for col in numeric_cols:
    X_train[col] = pd.to_numeric(X_train[col], errors="coerce")
    X_valid[col] = pd.to_numeric(X_valid[col], errors="coerce")
    median = X_train[col].median()
    if pd.isna(median):
        median = 0.0
    X_train[col] = X_train[col].fillna(median)
    X_valid[col] = X_valid[col].fillna(median)

try:
    from catboost import CatBoostClassifier

    probabilities = np.zeros(len(X_valid), dtype=float)
    for seed in (17, 41, 83):
        model = CatBoostClassifier(
            iterations=700,
            depth=7,
            learning_rate=0.045,
            loss_function="Logloss",
            eval_metric="Accuracy",
            l2_leaf_reg=6,
            random_seed=seed,
            random_strength=0.7,
            verbose=False,
            allow_writing_files=False,
            thread_count=-1,
        )
        model.fit(X_train, y, cat_features=categorical_cols)
        probabilities += model.predict_proba(X_valid)[:, 1] / 3.0
except ImportError:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

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
                                encoded_missing_value=-1,
                            ),
                        ),
                    ]
                ),
                categorical_cols,
            ),
            (
                "numeric",
                SimpleImputer(strategy="median"),
                numeric_cols,
            ),
        ],
        sparse_threshold=0,
    )

    X_encoded = transformer.fit_transform(X_train)
    valid_encoded = transformer.transform(X_valid)

    extra_trees = ExtraTreesClassifier(
        n_estimators=700,
        min_samples_leaf=2,
        max_features=0.8,
        class_weight="balanced",
        random_state=41,
        n_jobs=-1,
    )
    hist = HistGradientBoostingClassifier(
        learning_rate=0.055,
        max_iter=350,
        max_leaf_nodes=31,
        l2_regularization=2.0,
        random_state=83,
    )
    extra_trees.fit(X_encoded, y)
    hist.fit(X_encoded, y)
    probabilities = (
        0.55 * extra_trees.predict_proba(valid_encoded)[:, 1]
        + 0.45 * hist.predict_proba(valid_encoded)[:, 1]
    )

# Apply conservative companion evidence after modeling. Stronger evidence is
# used only when multiple labeled members of the same passenger group exist.
known = valid_group_count.to_numpy()
group_rate = X_valid["KnownGroupRate"].to_numpy(dtype=float)
group_weight = np.minimum(0.42, known / (known + 4.0))
probabilities = (1.0 - group_weight) * probabilities + group_weight * group_rate

submission = pd.DataFrame(
    {
        id_col: valid[id_col],
        target_col: probabilities >= 0.5,
    }
)
submission.to_csv(OUTPUT_PATH, index=False)
