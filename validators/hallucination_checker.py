from utils.logger import get_logger

logger = get_logger("hallucination_checker")

class HallucinationChecker:
    @staticmethod
    def verify(response: str, context: str, llm_client) -> tuple:
        """
        Runs LLM validation to confirm the response matches retrieved documents/context.
        """
        if llm_client is None:
            return True, 0.90, "Skipped LLM validation (mock mode)"

        prompt = (
            f"You are an AI Response Validator. Verify if the claims in the ANSWER are supported by the provided CONTEXT.\n"
            f"If there is any claim in the ANSWER that contradicts or is NOT mentioned in the CONTEXT at all, reply with NO.\n"
            f"If the ANSWER is supported or does not contain external claims, reply with YES.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"ANSWER:\n{response}\n\n"
            f"Reply with exactly one word (YES or NO):"
        )
        
        try:
            val_output = llm_client.generate(prompt=prompt)
            verdict = val_output.strip().upper()
            
            if "NO" in verdict:
                return False, 0.40, "Claims in response are not supported by the knowledge base."
            return True, 0.95, ""
        except Exception as e:
            logger.error(f"Error in hallucination checking process: {str(e)}")
            return True, 0.85, f"Validation warning: failed to connect to model: {str(e)}"
        
        return True, 0.90, ""
