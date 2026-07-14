import sqlite3
from typing import Generator
from app.config import Config
from utils.logger import get_logger

logger = get_logger("dependencies")

# Singletons for cached instances
_db_conn = None
_llm_model = None
_stt_model = None
_tts_model = None
_embedding_model = None
_rag_pipeline = None
_memory_manager = None
_persona_engine = None

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Provide an SQLite database connection.
    """
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(Config.SQLITE_DB_PATH, check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
        # Create tables if they do not exist
        _init_db(_db_conn)
    try:
        yield _db_conn
    finally:
        # We don't close the global connection, we keep it open for speed
        pass

def _init_db(conn: sqlite3.Connection):
    """
    Initialize memory and conversations tables.
    """
    cursor = conn.cursor()
    # Table for long term factual memory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS long_term_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fact_key TEXT UNIQUE,
        fact_val TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Table for chat logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        audio_path TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def get_llm():
    global _llm_model
    if _llm_model is None:
        from models.llm.gemini_model import GeminiModel
        _llm_model = GeminiModel()
    return _llm_model

def get_stt():
    global _stt_model
    if _stt_model is None:
        from models.stt.whisper_model import WhisperModel
        _stt_model = WhisperModel()
    return _stt_model

def get_tts():
    global _tts_model
    if _tts_model is None:
        from models.tts.xtts_model import XTTSModel
        _tts_model = XTTSModel()
    return _tts_model

def get_embeddings():
    global _embedding_model
    if _embedding_model is None:
        from models.embeddings.embedding_model import EmbeddingModel
        _embedding_model = EmbeddingModel()
    return _embedding_model

def get_persona_engine():
    global _persona_engine
    if _persona_engine is None:
        from personality.persona_engine import PersonaEngine
        _persona_engine = PersonaEngine()
    return _persona_engine

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        from memory.memory_manager import MemoryManager
        db_conn = next(get_db())
        _memory_manager = MemoryManager(db_conn)
    return _memory_manager

def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        from rag.rag_pipeline import RAGPipeline
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
