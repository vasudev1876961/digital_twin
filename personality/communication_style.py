from typing import List, Dict

class CommunicationStyle:
    def __init__(self, data: Dict = None):
        self.data = data or {}

    def get_greeting_templates(self) -> List[str]:
        return [
            "Hey! Vasu here.",
            "Hi, how can I help you today?",
            "Hey there, what's on your mind?",
            "Hey, glad you asked!"
        ]

    def format_to_style(self, text: str) -> str:
        """
        Post-processes a text response to align with Vasu's tone rules.
        """
        # Remove typical robotic starts like "As a digital replica of Vasu..."
        text = text.replace("As a digital replica of Vasu,", "Personally,")
        text = text.replace("As a digital twin of Vasu,", "I usually")
        
        # Strip trailing AI commentary
        if "Hopefully this answers your question" in text:
            text = text.replace("Hopefully this answers your question.", "")
            
        return text.strip()
