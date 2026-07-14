from typing import List, Dict

class ShortTermMemory:
    """
    Manages transient session context in RAM.
    """
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id][-limit:]

    def clear_history(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id] = []
