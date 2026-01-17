'''
settings.py: Holds all configuration details
'''
import os
from dotenv import load_dotenv

load_dotenv()

# config data for core.chunker.chunker.py
API_KEY = os.getenv('CHUNKER_API_KEY')
CHUNKER_MODEL = "openai/gpt-oss-120b"
JD_SKILL_MODEL = "llama-3.3-70b-versatile"
