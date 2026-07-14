import re

class PersonaConsistencyChecker:
    def __init__(self):
        self.forbidden_patterns = [
            r"as an AI",
            r"artificial intelligence",
            r"virtual assistant",
            r"language model",
            r"chatbot",
            r"developed by Google",
            r"created by Google",
            r"OpenAI",
            r"machine learning model"
        ]

    def verify_character(self, text: str) -> bool:
        """
        Verify that the model hasn't leaked generic AI helper phrases.
        """
        text_lower = text.lower()
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text_lower):
                return False
        return True

    def verify_first_person(self, text: str) -> bool:
        """
        Ensure responses use first-person and don't refer to Vasu in the third person.
        """
        text_stripped = text.strip()
        if text_stripped.startswith(("Vasu is", "Vasu has", "Vasu was", "Vasu graduated", "Vasu's project")):
            return False
            
        vasu_count = len(re.findall(r'\bVasu\b', text))
        i_count = len(re.findall(r'\b(I|me|my|mine|we)\b', text, re.IGNORECASE))
        if vasu_count > 2 and i_count == 0:
            return False
            
        return True
