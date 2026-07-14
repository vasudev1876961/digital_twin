import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Local Models
    WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "base")
    XTTS_SPEAKER_REF = os.getenv("XTTS_SPEAKER_REF", "voice_samples/reference/vasu_ref.wav")

    # DB Paths
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/sqlite/digital_twin.db")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "database/chroma")

    # Persona Configuration
    PERSONA_PROFILE = os.getenv("PERSONA_PROFILE", "vasu")

    # FastAPI Configurations
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Base Paths
    DOCUMENTS_DIR = BASE_DIR / "documents"
    VOICE_SAMPLES_DIR = BASE_DIR / "voice_samples"
    CONVERSATIONS_DIR = BASE_DIR / "conversations"

    # Ensure necessary folders exist
    @classmethod
    def ensure_directories(cls):
        dirs = [
            cls.DOCUMENTS_DIR / "resume",
            cls.DOCUMENTS_DIR / "projects",
            cls.DOCUMENTS_DIR / "certificates",
            cls.DOCUMENTS_DIR / "notes",
            cls.DOCUMENTS_DIR / "linkedin",
            cls.VOICE_SAMPLES_DIR / "raw",
            cls.VOICE_SAMPLES_DIR / "processed",
            cls.VOICE_SAMPLES_DIR / "reference",
            cls.CONVERSATIONS_DIR / "history",
            Path(cls.SQLITE_DB_PATH).parent,
            Path(cls.CHROMA_DB_PATH)
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

# Run directory check on import
Config.ensure_directories()
