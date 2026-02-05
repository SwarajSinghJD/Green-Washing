import re

ENV_KEYWORDS = [
    "carbon", "emission", "climate", "energy", "renewable",
    "net zero", "water", "waste", "biodiversity", "co2",
    "scope 1", "scope 2", "scope 3", "ghg"
]

METRIC_PATTERN = re.compile(
    r"\b\d+(\.\d+)?\s?(%|percent|co2|co2e|tco2e|tons?|tonnes?|gj|mw|mwh)\b",
    re.I
)

def remove_inline_junk(text: str) -> str:
    text = re.sub(r"\bPAGE\s*\d+\b", " ", text, flags=re.I)
    text = re.sub(r"-{2,}", " ", text)
    return text.strip()

def normalize_text(text: str) -> str:
    text = text.replace("CO₂", "CO2")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def reconstruct_sentences(lines):
    sentences = []
    buffer = ""

    for line in lines:
        if not buffer:
            buffer = line
            continue

        if buffer.endswith((".", "!", "?")):
            sentences.append(buffer)
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        sentences.append(buffer)

    return sentences

def is_environment_relevant(sentence: str) -> bool:
    s = sentence.lower()
    return any(k in s for k in ENV_KEYWORDS)

def has_metric(sentence: str) -> bool:
    return bool(METRIC_PATTERN.search(sentence))
