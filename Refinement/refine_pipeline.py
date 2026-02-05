import os
import json
import re
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

from patterns import GLOSSARY_REGEX, METRIC_REGEX

INPUT_DIR = os.path.join(BASE_DIR, "input_jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_jsonl")
os.makedirs(OUTPUT_DIR, exist_ok=True)



# -------------------------
# HELPERS
# -------------------------

GOVERNANCE_WORDS = [
    "board", "committee", "oversight", "governance",
    "reviewed", "approved", "audit"
]

SPLIT_CONNECTORS = [
    r"\band\b",
    r"\bwhile\b",
    r"\bas part of\b",
    r"\bas well as\b"
]


def is_glossary_sentence(sentence: str) -> bool:
    return bool(GLOSSARY_REGEX.search(sentence))


def has_metric(sentence: str) -> bool:
    return bool(METRIC_REGEX.search(sentence))


def is_governance(sentence: str) -> bool:
    s = sentence.lower()
    return any(w in s for w in GOVERNANCE_WORDS)


# -------------------------
# BALANCED SENTENCE SPLIT
# -------------------------

def balanced_split(sentence: str):
    """
    Split sentence ONLY if:
    - it contains a metric AND
    - contains governance or multiple clauses
    """
    if not has_metric(sentence):
        return [sentence]

    parts = [sentence]

    for connector in SPLIT_CONNECTORS:
        new_parts = []
        for p in parts:
            split = re.split(connector, p, flags=re.I)
            if len(split) > 1:
                for s in split:
                    s = s.strip()
                    if len(s) > 25:
                        new_parts.append(s)
            else:
                new_parts.append(p)
        parts = new_parts

    return parts


# -------------------------
# RECLASSIFICATION
# -------------------------

def classify(sentence: str, metric: bool) -> str:
    s = sentence.lower()

    if is_governance(sentence):
        return "governance"

    if metric:
        return "metric"

    if any(w in s for w in ["aim", "target", "commit", "goal", "aspire"]):
        return "vision"

    if any(w in s for w in ["reduced", "achieved", "implemented", "installed"]):
        return "action"

    if any(w in s for w in ["leader", "best-in-class", "world-class"]):
        return "marketing"

    return "other"


# -------------------------
# MAIN REFINEMENT
# -------------------------

def refine_file(path):
    refined = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            sentence = row["sentence"]

            # 1. Drop glossary junk
            if is_glossary_sentence(sentence):
                continue

            # 2. Balanced split
            split_sentences = balanced_split(sentence)

            for s in split_sentences:
                s = re.sub(r"\s+", " ", s).strip()

                if len(s) < 30:
                    continue

                metric = has_metric(s)
                category = classify(s, metric)

                refined.append({
                    "company": row["company"],
                    "year": row["year"],
                    "sentence": s,
                    "category": category,
                    "has_metric": metric,
                    "env_relevant": row["env_relevant"]
                })

    return refined


# -------------------------
# RUN ALL
# -------------------------

def run_all():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue

        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(OUTPUT_DIR, fname)

        refined = refine_file(in_path)

        with open(out_path, "w", encoding="utf-8") as f:
            for r in refined:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"✅ {fname}: {len(refined)} balanced-clean sentences")


if __name__ == "__main__":
    run_all()
