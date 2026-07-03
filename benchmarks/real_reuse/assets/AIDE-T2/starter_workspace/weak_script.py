import csv
from collections import Counter

TARGET = "Transported"
ID = "PassengerId"

with open("train.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

label = Counter(row[TARGET] for row in rows).most_common(1)[0][0]

with open("validation_features.csv", newline="", encoding="utf-8") as handle:
    features = list(csv.DictReader(handle))

with open("submission.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=[ID, TARGET])
    writer.writeheader()
    for row in features:
        writer.writerow({ID: row[ID], TARGET: label})
