from cleaning_pipeline import (
    remove_inline_junk,
    normalize_text,
    reconstruct_sentences,
    is_environment_relevant,
    has_metric
)

from atomic_extractor import explode_sentence

def pdf_text_to_atomic_sentences(raw_text: str):
    lines = raw_text.split("\n")

    cleaned_lines = []
    for line in lines:
        line = remove_inline_junk(line)
        line = normalize_text(line)
        if line:
            cleaned_lines.append(line)

    sentences = reconstruct_sentences(cleaned_lines)

    atomic_sentences = []

    for s in sentences:
        if len(s) < 30 or len(s) > 400:
            continue
        if not (is_environment_relevant(s) or has_metric(s)):
            continue

        exploded = explode_sentence(s)
        if exploded:
            atomic_sentences.extend(exploded)
        else:
            atomic_sentences.append(s)

    return atomic_sentences
