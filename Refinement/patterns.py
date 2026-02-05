import re

# ---- GLOSSARY / TABLE DEFINITIONS ----
GLOSSARY_PATTERNS = [
    r"carbon dioxide equivalent",
    r"\bco2e\b",
    r"\bmmboe\b",
    r"million barrels of oil equivalent",
    r"\bnox\b",
    r"\bsox\b",
    r"\bvoc\b",
    r"metric tons?",
    r"abbreviations?",
    r"definitions?",
]

GLOSSARY_REGEX = re.compile("|".join(GLOSSARY_PATTERNS), re.I)


# ---- METRIC PATTERNS (ROBUST) ----
METRIC_REGEX = re.compile(
    r"""
    (
        \d+(\.\d+)?            # number
        \s*[-–to]*\s*
        \d*(\.\d+)?            # optional range
        \s*
        (%|percent|
        tco2e|co2e|co2|
        tonnes?|tons?|
        gj|mj|mw|mwh)
    )
    """,
    re.I | re.X
)


# ---- SENTENCE SPLIT PROTECTION ----
BAD_MERGE_PATTERNS = [
    r"\bteam\b.*\bpercent\b",
    r"\bcommittee\b.*\bco2\b",
]
