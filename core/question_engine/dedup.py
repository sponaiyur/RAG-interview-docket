from difflib import SequenceMatcher

def is_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold

def deduplicate_by_level(questions):
    """
    Deduplicate questions within the same level.
    """
    result = []
    seen = {}

    for q in questions:
        level = q["level"]
        seen.setdefault(level, [])

        if not any(is_similar(q["question"], s) for s in seen[level]):
            seen[level].append(q["question"])
            result.append(q)

    return result
