from difflib import SequenceMatcher

def score_answer(actual: str, expected: str) -> tuple[float, bool]:
    """
    Return similarity ratio and pass flag if >=0.9
    """
    a = actual.strip().lower()
    e = expected.strip().lower()
    ratio = SequenceMatcher(None, a, e).ratio()
    return ratio, ratio >= 0.9
