'''
generator.py: Generate the final questions, send this to the frontend for display.
'''

from core.question_engine.engine import generate_questions

def generate_questions_from_chunks(chunks: list):
    """
    Takes a list of chunk dicts (from AgenticChunker),
    extracts claims, generates questions using the engine,
    and returns a structured result.
    """
    output = []

    import concurrent.futures

    # Flatten all claims first to make parallelization easier
    all_claims = []
    for chunk in chunks:
        skill = chunk.get("focus_skill", "Unknown")
        claims = chunk.get("claims", [])
        for c in claims:
            claim_text = c.get("claim_text")
            if claim_text:
                all_claims.append({
                    "chunk_id": chunk.get("chunk_id"),
                    "skill": skill,
                    "claim_text": claim_text
                })

    total_claims = len(all_claims)
    print(f"Parallelizing generation for {total_claims} claims...")
    
    # Store results by chunk_id for re-assembly
    results_by_chunk = {}

    def process_claim(item):
        print(f"Processing claim for {item['skill']}...")
        result = generate_questions(item['claim_text'])
        return item['chunk_id'], item['skill'], result

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_claim, item) for item in all_claims]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                chunk_id, skill, result = future.result()
                print(f"Completed {i+1}/{total_claims} claims")
                # Yield result PLUS progress info
                yield (chunk_id, skill, result, i + 1, total_claims)
            except Exception as e:
                print(f"Error processing claim: {e}")

    # No longer returning the full list at the end, as we are yielding
    return