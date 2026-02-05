import re

# ---------- HARD JUNK PATTERNS ----------
PAGE_PATTERNS = [
    r"---\s*PAGE\s*\d+\s*---",
    r"^\s*PAGE\s*\d+",
    r"^\s*\d+\s*$"
]

SECTION_HEADERS = [
    r"^[A-Z\s&]{6,}$",            # ALL CAPS headers
    r"^Contents$",
    r"^Introduction$",
    r"^Governance$",
    r"^Performance$"
]

TABLE_NOISE = [
    r"\bFY\s?\d{4}[-–]\d{2}\b",
    r"\b₹|\bUSD\b|\bUS\$\b",
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
