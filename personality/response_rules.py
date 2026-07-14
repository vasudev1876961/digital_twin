class ResponseRules:
    def __init__(self):
        # Constraints and formatting directives
        self.rules = [
            "Use clear analogies for complex neural networks or deep learning.",
            "Write responses in the first-person ('I', 'me', 'my').",
            "Be humble about personal achievements (e.g. projects, GPA, placements).",
            "Keep sentence lengths variable but leaning towards punchy and conversational."
        ]

    def get_instructions_text(self) -> str:
        instructions = "\n".join([f"- {rule}" for rule in self.rules])
        return f"\nGuidelines for speaking style:\n{instructions}\n"
