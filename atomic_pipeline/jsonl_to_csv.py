import os
import json
import csv
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, "input_jsonl")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "combined_esg_final.csv")


rows = []
all_fields = set()

# -------------------------
# READ ALL JSONL FILES
# -------------------------

for fname in os.listdir(INPUT_DIR):
    if not fname.endswith(".jsonl"):
        continue

    path = os.path.join(INPUT_DIR, fname)

    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            row = json.loads(line)
            row["source_file"] = fname  # track origin
            rows.append(row)
            all_fields.update(row.keys())

print(f"📦 Total rows collected: {len(rows)}")

# -------------------------
# WRITE COMBINED CSV
# -------------------------

fieldnames = sorted(all_fields)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"✅ Combined CSV written to: {OUTPUT_FILE}")
