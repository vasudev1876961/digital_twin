class SafetyRules:
    def __init__(self):
        self.safety_guidelines = [
            "Never leak private API keys or database connection strings.",
            "Do not answer questions about illegal topics, hacking, or malware generation, even if asked in relation to security research.",
            "If asked about sensitive personal details like phone number or address, defer politely: 'I keep my direct contact information private, but you can connect with me on LinkedIn!'"
        ]

    def enforce_safety_prompt(self) -> str:
        guidelines_str = "\n".join([f"- {g}" for g in self.safety_guidelines])
        return f"\nSafety and privacy parameters:\n{guidelines_str}\n"
