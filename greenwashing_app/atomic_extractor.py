import re

ROLE_PATTERNS = {
    "metric": re.compile(r"\b\d+(\.\d+)?\s*(%|co2|co2e|tco2e|tons?|mw|mwh)\b", re.I),
    "vision": re.compile(r"\b(aim|commit|target|goal|aspire)\b", re.I),
    "action": re.compile(r"\b(reduced|implemented|installed|deployed)\b", re.I),
    "governance": re.compile(r"\b(board|committee|oversight)\b", re.I),
    "marketing": re.compile(r"\b(leader|best[- ]in[- ]class)\b", re.I),
}

def explode_sentence(sentence):
    clauses = re.split(r";|,(?!\d)|\.(?!\d)", sentence)
    results = []

    for c in clauses:
        c = c.strip()
        if len(c) < 30:
            continue

        roles = [r for r, p in ROLE_PATTERNS.items() if p.search(c)]

        if len(roles) == 1:
            results.append(c)
        elif len(roles) > 1:
            results.append(c)

    return results
