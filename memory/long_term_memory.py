import sqlite3
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger("long_term_memory")

class LongTermMemory:
    """
    Manages long-term factual memories stored persistently in SQLite.
    """
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_fact(self, key: str, value: str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO long_term_memory (fact_key, fact_val, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, value)
            )
            self.conn.commit()
            logger.info(f"Saved long-term fact to SQLite: {key}")
        except Exception as e:
            logger.error(f"Failed to write fact to SQLite: {str(e)}")

    def get_all_facts(self) -> Dict[str, str]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT fact_key, fact_val FROM long_term_memory")
            rows = cursor.fetchall()
            return {r["fact_key"]: r["fact_val"] for r in rows}
        except Exception as e:
            logger.error(f"Failed to fetch SQLite facts: {str(e)}")
            return {}
