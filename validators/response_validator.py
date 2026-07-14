from typing import List, Dict
from validators.hallucination_checker import HallucinationChecker
from validators.persona_consistency import PersonaConsistencyChecker
from utils.logger import get_logger

logger = get_logger("response_validator")

class ResponseValidator:
    def __init__(self):
        self.consistency_checker = PersonaConsistencyChecker()

    def validate_response(
        self,
        query: str,
        response: str,
        rag_context: str = "",
        memories: List[str] = [],
        llm_client = None
    ) -> Dict[str, any]:
        """
        Runs comprehensive validation checks using specialized validator classes.
        """
        logger.info("Running response validation layer...")

        # 1. Check AI Leakage
        if not self.consistency_checker.verify_character(response):
            logger.warning("Persona consistency check failed: AI helper phrase detected.")
            return {
                "is_valid": False,
                "confidence": 0.3,
                "reason": "Persona check failed: response contains AI helper phrases.",
                "validated_response": "I don't have enough information to answer that as Vasu."
            }

        # 2. Check Third Person Leakage
        if not self.consistency_checker.verify_first_person(response):
            logger.warning("Persona consistency check failed: referred to Vasu in the third person.")
            return {
                "is_valid": False,
                "confidence": 0.4,
                "reason": "Persona check failed: answered in the third person instead of first person.",
                "validated_response": "I don't have enough information to answer that as Vasu."
            }

        # 3. Check Hallucinations
        is_consistent = True
        hallucination_reason = ""
        confidence_score = 0.95

        if rag_context or memories:
            context_string = f"{rag_context}\n\nMemories:\n" + "\n".join(memories)
            is_consistent, confidence_score, hallucination_reason = HallucinationChecker.verify(
                response=response,
                context=context_string,
                llm_client=llm_client
            )

        if not is_consistent:
            logger.warning(f"Hallucination checker flagged response: {hallucination_reason}")
            return {
                "is_valid": False,
                "confidence": confidence_score,
                "reason": f"Hallucination check failed: {hallucination_reason}",
                "validated_response": "I don't have enough information to answer that as Vasu."
            }

        logger.info(f"Response validation passed. Confidence: {confidence_score}")
        return {
            "is_valid": True,
            "confidence": confidence_score,
            "reason": "Passed all validation tests.",
            "validated_response": response
        }
