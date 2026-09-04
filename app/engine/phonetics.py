import jellyfish
from rapidfuzz import fuzz

def normalize_phonetic_input(text: str) -> str:
    cleaned = text.strip().lower()
    # Handle W/V phoneme merger common in ASR transcription & Indian English
    return cleaned.replace("w", "v")

def compute_phonetic_signatures(term: str) -> dict:
    norm = normalize_phonetic_input(term)
    return {
        "soundex": jellyfish.soundex(norm) if norm else "",
        "metaphone": jellyfish.metaphone(norm) if norm else "",
        "nysiis": jellyfish.nysiis(norm) if norm else ""
    }

def match_score(candidate: str, canonical: str) -> tuple[bool, float, str]:
    c_raw = candidate.strip().lower()
    t_raw = canonical.strip().lower()

    if c_raw == t_raw:
        return True, 1.0, "exact_match"

    # Normalized versions (w -> v)
    c_norm = normalize_phonetic_input(c_raw)
    t_norm = normalize_phonetic_input(t_raw)

    if c_norm == t_norm:
        return True, 0.98, "v_w_equivalence"

    # Metaphone comparison
    m_cand = jellyfish.metaphone(c_norm)
    m_canon = jellyfish.metaphone(t_norm)
    if m_cand and m_canon and m_cand == m_canon:
        return True, 0.95, "metaphone_match"

    # NYSIIS comparison
    ny_cand = jellyfish.nysiis(c_norm)
    ny_canon = jellyfish.nysiis(t_norm)
    if ny_cand and ny_canon and ny_cand == ny_canon:
        return True, 0.90, "nysiis_match"

    # String edit distance fallback
    ratio = fuzz.ratio(c_norm, t_norm) / 100.0
    if ratio >= 0.75:
        return True, ratio, "fuzzy_match"

    return False, ratio, "no_match"