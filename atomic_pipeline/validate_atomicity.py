import json
import os
from statistics import mean
BASE_DIR = os.path.dirname(__file__)
DIR = os.path.join(BASE_DIR, "output_atomic_jsonl")


lengths = []
mixed_role_violations = 0
total = 0

for fname in os.listdir(DIR):
    if not fname.endswith(".jsonl"):
        continue

    with open(os.path.join(DIR, fname), encoding="utf-8", errors="ignore") as f:
        for line in f:
            row = json.loads(line)
            total += 1
            lengths.append(len(row["sentence"]))

            # Rule: metric sentences must NOT mention governance
            if row["category"] == "metric":
                if any(w in row["sentence"].lower()
                       for w in ["board", "committee", "oversight", "governance"]):
                    mixed_role_violations += 1

print("Total sentences:", total)
print("Average sentence length:", int(mean(lengths)))
print("Mixed-role violations:", mixed_role_violations)
