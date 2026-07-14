import sqlite3
from typing import List, Dict
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory
from memory.semantic_memory import SemanticMemory
from utils.logger import get_logger

logger = get_logger("memory_manager")

class MemoryManager:
    """
    Unified Orchestrator for all three memory systems:
    1. Short-Term (RAM session sliding window)
    2. Long-Term persistent facts (SQLite db)
    3. Semantic/episodic context retrieval (ChromaDB)
    """
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_conn)
        self.semantic = SemanticMemory()

    def add_message(self, session_id: str, role: str, content: str, audio_path: str = None):
        """
        Record a chat message in short-term RAM context AND persist to SQLite logs.
        """
        try:
            # 1. RAM Cache (Short Term)
            self.short_term.add_message(session_id, role, content)
            
            # 2. SQLite persistent chat log
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, role, content, audio_path) VALUES (?, ?, ?, ?)",
                (session_id, role, content, audio_path)
            )
            self.conn.commit()
            logger.info(f"Saved message from {role} to short-term database & session memory.")
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")

    def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Try to load from Short-Term RAM cache, fallback to SQLite.
        """
        history = self.short_term.get_history(session_id, limit)
        if history:
            return history

        # Fallback to database
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            loaded_history = [{"role": r["role"], "content": r["content"]} for r in rows]
            
            # Populate RAM cache
            for msg in loaded_history:
                self.short_term.add_message(session_id, msg["role"], msg["content"])
                
            return loaded_history
        except Exception as e:
            logger.error(f"Error reading chat history: {str(e)}")
            return []

    def save_fact(self, fact_key: str, fact_val: str):
        self.long_term.save_fact(fact_key, fact_val)

    def get_relevant_facts(self, query: str) -> List[str]:
        """
        Searches both Long-Term factual SQLite and Semantic Chroma memories.
        """
        relevant = []
        
        # 1. Query Long Term SQLite memory
        facts = self.long_term.get_all_facts()
        if not facts:
            self._seed_default_facts()
            facts = self.long_term.get_all_facts()

        query_lower = query.lower()
        for k, v in facts.items():
            if k.lower() in query_lower or any(word in query_lower for word in k.replace("_", " ").split()):
                relevant.append(f"{k}: {v}")

        # 2. Query Semantic Chroma memories
        semantic_hits = self.semantic.search_memories(query, limit=2)
        for hit in semantic_hits:
            relevant.append(f"Semantic Experience: {hit}")

        logger.info(f"Retrieved {len(relevant)} memory references.")
        return relevant

    def _seed_default_facts(self):
        defaults = {
            "hobby": "Vasu loves playing Volleyball in his free time.",
            "status": "Vasu is currently preparing for college campus placements.",
            "favourite_project": "The malware detection project utilizing deep learning models.",
            "location": "Vasu is based out of India.",
            "skills": "Vasu is skilled in machine learning, PyTorch, audio processing, and Python software engineering.",
            "twin_status": "Vasu created this Digital Human Twin as a personalized conversational AI replica."
        }
        for k, v in defaults.items():
            self.save_fact(k, v)
