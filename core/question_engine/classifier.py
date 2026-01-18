def classify_claim(claim: str) -> str:
    c = claim.lower()

    if any(w in c for w in ["optimize", "optimized", "improved", "reduced"]):
        return "OPTIMIZATION"
    if any(w in c for w in ["design", "architect"]):
        return "DESIGN"
    if any(w in c for w in ["implement", "implemented", "built", "developed","trained"]):
        return "IMPLEMENTATION"
    if any(w in c for w in ["use", "used", "applied", "worked",]):
        return "USAGE"

    return "GENERAL"
