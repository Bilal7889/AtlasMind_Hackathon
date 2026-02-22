"""
Configuration and constants for AtlasMind
"""

import os
from dotenv import load_dotenv

# Load local .env file if it exists
load_dotenv()

# ==================== API Configuration ====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    # This prevents "Silent Failures" where the app runs but AI calls fail.
    print("WARNING: GROQ_API_KEY not found in environment variables.")

MODEL_NAME = "llama-3.1-8b-instant"

# ==================== Vector Database Configuration ====================
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# ==================== Quiz Configuration ====================
QUIZ_CONTEXT_LENGTH = 6000
TRANSCRIPT_PREVIEW_LENGTH = 8000

# ==================== UI Configuration ====================
APP_TITLE = "AtlasMind"
APP_DESCRIPTION = "Transform YouTube lectures and PDF documents into interactive learning experiences using RAG"
APP_SUBTITLE = "Using yt-dlp for reliable transcript fetching"