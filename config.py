import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is missing. "
        "Please provide a valid PostgreSQL connection string in environment or .env file."
    )

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

HF_TOKEN = os.getenv("HF_TOKEN")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-tiny")
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "superb/wav2vec2-base-superb-er")
LLM_MODEL = os.getenv("LLM_MODEL", "google/flan-t5-base")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./rag/vector_store")

def get_hf_token():
    token = os.getenv("HF_TOKEN")
    if token and token.strip() and token.strip() != "your_huggingface_token_here":
        return token.strip()
    return None