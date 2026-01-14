'''
templates.py: Create simple question templates. 
- Call this file to generate questions, don't write templates anywhere else
- example template (this is to be refined further):
QUESTION_TEMPLATES = {
    "clarification": {
        "intent": "validate claim",
        "structure": "You mentioned {claim}. Can you explain how it works?"
    },
    "deep_probe": {
        "intent": "test depth",
        "structure": "What design decisions did you make while implementing {claim}?"
    }
}

'''