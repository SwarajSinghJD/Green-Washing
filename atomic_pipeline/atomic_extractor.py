import os
import json
import re

import sys
BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

INPUT_DIR = os.path.join(BASE_DIR, "input_jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_atomic_jsonl")

# =========================
# ROLE DEFINITIONS (GLOBAL)
# =========================

ROLE_PATTERNS = {
    "metric": re.compile(
        r"\b\d+(\.\d+)?\s*(%|percent|co2|co2e|tco2e|tons?|tonnes?|gj|mw|mwh)\b",
        re.I
    ),
    "vision": re.compile(
        r"\b(aim|commit|aspire|goal|target|pledge|vision|ambition)\b",
        re.I
    ),
    "action": re.compile(
        r"\b(reduce|reduced|implement|implemented|install|installed|deploy|improve|invest|transition)\b",
        re.I
    ),
    "governance": re.compile(
        r"\b(board|committee|oversight|governance|leadership|approved|reviewed)\b",
        re.I
    ),
    "marketing": re.compile(
        r"\b(leader|best[- ]in[- ]class|world[- ]class|premier)\b",
        re.I
    ),
}

# =========================
# SENTENCE NORMALIZATION
# =========================

def normalize(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# =========================
# ATOMIC ROLE EXTRACTION
# =========================

def explode_sentence(sentence):
    """
    Split a sentence into role-pure atomic claims.
    """
    # clauses = re.split(r",|;|\.", sentence)
    clauses = re.split(r";|,(?!\d)|\.(?!\d)", sentence)
    extracted = []

    for clause in clauses:
        clause = normalize(clause)
        if len(clause) < 30:
            continue

        matched_roles = [
            role for role, pat in ROLE_PATTERNS.items()
            if pat.search(clause)
        ]

        # If clause clearly maps to ONE role → keep it
        if len(matched_roles) == 1:
            extracted.append((matched_roles[0], clause))

        # If multiple roles → split by priority
        elif len(matched_roles) > 1:
            for role in matched_roles:
                extracted.append((role, clause))

    return extracted


# =========================
# FILE PROCESSING
# =========================

def process_file(path):
    atomic_rows = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            sentence = normalize(row["sentence"])

            exploded = explode_sentence(sentence)

            # If explosion succeeded → replace original
            if exploded:
                for role, text in exploded:
                    atomic_rows.append({
                        "company": row["company"],
                        "year": row["year"],
                        "sentence": text,
                        "category": role,
                        "has_metric": role == "metric",
                        "env_relevant": True
                    })
            else:
                # Keep sentence only if already atomic
                atomic_rows.append(row)

    return atomic_rows



# =========================
# RUN FOR ALL FILES
# =========================

def run_all():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue

        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(OUTPUT_DIR, fname)

        atomic = process_file(in_path)

        with open(out_path, "w", encoding="utf-8") as f:
            for r in atomic:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"🔥 {fname}: {len(atomic)} atomic claims created")


if __name__ == "__main__":
    run_all()
