'''
retriever.py: Strips chunk metadata and prepares data for question_engine
'''


def strip_chunks(chunks: list) -> None:
    """
    Strip metadata from chunks, keeping only essential data for question_engine.
    """
    stripped = []
    for chunk in chunks:
        stripped.append({
            "chunk_id": chunk["chunk_id"],
            "focus_skill": chunk["focus_skill"],
            "claims": [
                {
                    "claim_text": c["claim_text"],
                    "source_section": c["source_section"]
                }
                for c in chunk.get("claims", [])
            ]
        })
    return stripped