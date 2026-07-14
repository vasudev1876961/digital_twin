import os
import json
from pathlib import Path
from app.config import Config
from utils.logger import get_logger

logger = get_logger("persona_engine")

class PersonaEngine:
    def __init__(self):
        self.persona_name = Config.PERSONA_PROFILE
        self.profile_path = Path(__file__).parent / "personality_profiles" / f"{self.persona_name}.json"
        self.persona_data = self._load_persona_profile()

    def _load_persona_profile(self) -> dict:
        # Create directory and profile if not exist
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.profile_path.exists():
            default_profile = {
                "name": "Vasu",
                "communication_style": {
                    "vocabulary": "Technical, intuitive, friendly",
                    "technical_depth": "High, but explains concepts using simple analogies",
                    "humor_level": "Subtle, technical, humble",
                    "greeting_style": "Casual, e.g., 'Hey there!', 'Hi, how can I help?'",
                    "formality": "Semi-formal to casual",
                    "sentence_length": "Short-to-medium",
                    "frequently_used_phrases": [
                        "I usually explain this as...", 
                        "Think of it this way...", 
                        "Basically...", 
                        "From my experience..."
                    ]
                },
                "interests": ["Machine Learning", "Software Engineering", "Volleyball", "Malware Detection"],
                "values": ["Continuous learning", "Simplicity", "Explainable AI", "Practical applications"]
            }
            with open(self.profile_path, "w") as f:
                json.dump(default_profile, f, indent=4)
            logger.info(f"Created default persona profile at: {self.profile_path}")
            return default_profile
        
        try:
            with open(self.profile_path, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded persona profile: {self.persona_name}")
                return data
        except Exception as e:
            logger.error(f"Error loading persona profile: {str(e)}")
            return {}

    def get_system_instructions(self) -> str:
        """
        Builds the system instructions context for Gemini.
        """
        style = self.persona_data.get("communication_style", {})
        phrases = ", ".join([f"'{p}'" for p in style.get("frequently_used_phrases", [])])
        
        instructions = (
            f"You are the digital human twin of {self.persona_data.get('name', 'Vasu')}.\n"
            f"You must answer questions AS {self.persona_data.get('name', 'Vasu')}, in the first person ('I', 'me', 'my').\n"
            f"Never break character or refer to yourself as an AI assistant.\n\n"
            f"Here is your personality and speaking profile:\n"
            f"- Vocabulary: {style.get('vocabulary')}\n"
            f"- Technical Depth: {style.get('technical_depth')}\n"
            f"- Humor: {style.get('humor_level')}\n"
            f"- Greeting: {style.get('greeting_style')}\n"
            f"- Preferred sentence length: {style.get('sentence_length')}\n"
            f"- Interests: {', '.join(self.persona_data.get('interests', []))}\n"
            f"- Core values: {', '.join(self.persona_data.get('values', []))}\n\n"
            f"Frequently used phrases you like to incorporate naturally: {phrases}.\n\n"
            f"Rules:\n"
            f"1. If a question is personal, answer using the retrieved context from your memories and knowledge base.\n"
            f"2. Speak in a clean, professional yet conversational tone.\n"
            f"3. Do not make up facts. If you do not know the answer, say: 'I don't have enough information to answer that as Vasu.'\n"
        )
        return instructions
