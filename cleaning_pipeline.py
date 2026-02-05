import os
import json
import re

# ==============================
# CONFIG
# ==============================

RAW_DIR = "raw_txt"
OUT_DIR = "cleaned_jsonl"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- HARD JUNK PATTERNS ----------
PAGE_PATTERNS = [
    r"---\s*PAGE\s*\d+\s*---",
    r"\bPAGE\s*\d+\b"
]

SECTION_HEADERS = [
    r"^[A-Z\s&/]{6,}$",     # ALL CAPS headers
    r"^CONTENTS?$",
    r"^INTRODUCTION$",
    r"^GOVERNANCE$",
    r"^PERFORMANCE$",
]

# ---------- ESG KEYWORDS ----------
ENV_KEYWORDS = [
    "carbon", "emission", "climate", "energy", "renewable",
    "net zero", "water", "waste", "biodiversity", "decarbon",
    "co2", "scope 1", "scope 2", "scope 3", "ghg"
]

METRIC_PATTERN = re.compile(
    r"\b\d+(\.\d+)?\s?(%|percent|tco2e|co2|tons?|tonnes?|gj|mw|mwh|years?)\b",
    re.I
)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")


# ==============================
# JUNK REMOVAL
# ==============================

def is_junk_line(line: str) -> bool:
    line = line.strip()
    if not line:
        return True

    for pat in SECTION_HEADERS:
        if re.match(pat, line):
            return True

    return False


def remove_inline_junk(text: str) -> str:
    # Remove PAGE markers anywhere in line
    text = re.sub(r"---\s*PAGE\s*\d+\s*---", " ", text, flags=re.I)
    text = re.sub(r"\bPAGE\s*\d+\b", " ", text, flags=re.I)

    # Remove standalone page numbers before PAGE markers
    text = re.sub(r"\b\d+\s*(?=PAGE)", " ", text)

    # Remove leftover dashed separators
    text = re.sub(r"-{2,}", " ", text)

    return text.strip()


def normalize_text(text: str) -> str:
    text = text.replace("CO₂", "CO2")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ==============================
# SENTENCE RECONSTRUCTION
# ==============================

def reconstruct_sentences(lines):
    sentences = []
    buffer = ""

    for line in lines:
        line = normalize_text(line)

        if not buffer:
            buffer = line
            continue

        if re.search(r"[.!?]$", buffer):
            sentences.append(buffer)
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        sentences.append(buffer)

    return sentences


# ==============================
# ESG FILTERING
# ==============================

def is_environment_relevant(sentence: str) -> bool:
    s = sentence.lower()
    return any(k in s for k in ENV_KEYWORDS)


def has_metric(sentence: str) -> bool:
    return bool(METRIC_PATTERN.search(sentence))


# ==============================
# CLAIM CLASSIFICATION
# ==============================

def classify_sentence(sentence: str) -> str:
    s = sentence.lower()

    if any(w in s for w in ["aim", "vision", "commit", "aspire", "target", "goal"]):
        return "vision"

    if any(w in s for w in ["reduced", "achieved", "installed", "implemented", "deployed"]):
        return "action"

    if has_metric(sentence):
        return "metric"

    if any(w in s for w in ["board", "committee", "governance", "oversight"]):
        return "governance"

    if any(w in s for w in ["leader", "best-in-class", "world-class", "premier"]):
        return "marketing"

    return "other"


# ==============================
# FILE METADATA
# ==============================

def extract_company_year(filename):
    base = os.path.basename(filename).replace(".txt", "")
    tokens = base.split("_")

    year = None
    company_tokens = []

    for t in tokens:
        if re.fullmatch(r"(19|20)\d{2}", t):
            year = int(t)
        elif not t.isdigit():
            company_tokens.append(t)

    company = "_".join(company_tokens).upper() if company_tokens else "UNKNOWN"
    return company, year


# ==============================
# MAIN PIPELINE
# ==============================

def process_file(path):
    company, year = extract_company_year(path)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = f.readlines()

    cleaned_lines = []

    for line in raw_lines:
        if is_junk_line(line):
            continue

        line = remove_inline_junk(line)
        line = normalize_text(line)

        if line:
            cleaned_lines.append(line)

    sentences = reconstruct_sentences(cleaned_lines)

    records = []
    seen = set()

    for sent in sentences:
        sent = normalize_text(sent)

        if len(sent) < 30 or len(sent) > 400:
            continue

        key = sent.lower()
        if key in seen:
            continue
        seen.add(key)

        env = is_environment_relevant(sent)
        metric = has_metric(sent)

        if not env and not metric:
            continue

        record = {
            "company": company,
            "year": year,
            "sentence": sent,
            "category": classify_sentence(sent),
            "has_metric": metric,
            "env_relevant": env
        }

        records.append(record)

    return records


# ==============================
# RUN ALL FILES
# ==============================

def run_all():
    for fname in os.listdir(RAW_DIR):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(RAW_DIR, fname)
        records = process_file(path)

        out_path = os.path.join(
            OUT_DIR, fname.replace(".txt", ".jsonl")
        )

        with open(out_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"✅ {fname}: {len(records)} clean sentences")


if __name__ == "__main__":
    run_all()
