class ReasoningTrace:
    @staticmethod
    def generate_log(query: str, has_rag: bool, has_memories: bool, is_valid: bool) -> str:
        logs = ["Reasoning Path Log:"]
        logs.append(f"- Received query: '{query}'")
        
        if has_rag:
            logs.append("- RAG pipeline executed successfully; matched relevant documents.")
        else:
            logs.append("- RAG pipeline skipped or found no matches.")

        if has_memories:
            logs.append("- SQLite long-term memory matched personal keyword facts.")
        else:
            logs.append("- SQLite memory scanner returned no keyword hits.")

        if is_valid:
            logs.append("- Response validation passed. No persona deviations or contradictions detected.")
        else:
            logs.append("- Response validation failed. Replaced answer with fallback token response.")

        return "\n".join(logs)
