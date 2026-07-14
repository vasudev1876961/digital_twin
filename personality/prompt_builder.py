from typing import List, Dict

class PromptBuilder:
    @staticmethod
    def build_prompt(
        query: str,
        rag_context: str = "",
        memories: List[str] = [],
        chat_history: List[Dict[str, str]] = []
    ) -> str:
        """
        Synthesizes the prompt parts into a single cohesive message for the LLM.
        """
        sections = []

        # Add context from documents (RAG)
        if rag_context:
            sections.append(
                "--- RETRIEVED PERSONAL DOCUMENTS & PROJECTS ---\n"
                f"{rag_context}\n"
                "------------------------------------------------"
            )

        # Add retrieved long-term memories
        if memories:
            memories_str = "\n".join([f"- {m}" for m in memories])
            sections.append(
                "--- RETRIEVED MEMORIES & PERSONAL FACTS ---\n"
                f"{memories_str}\n"
                "--------------------------------------------"
            )

        # Add conversational chat history (recent messages)
        if chat_history:
            history_str = ""
            for msg in chat_history[-6:]: # Limit to last 6 messages
                role_label = "Vasu (You)" if msg["role"] == "assistant" else "Interviewer"
                history_str += f"{role_label}: {msg['content']}\n"
            sections.append(
                "--- RECENT CONVERSATION HISTORY ---\n"
                f"{history_str}"
                "-----------------------------------"
            )

        # Add instructions and user's query
        sections.append(
            f"Interviewer: {query}\n"
            "Vasu:"
        )

        return "\n\n".join(sections)
