from typing import List, Dict
from explainability.confidence import ConfidenceEstimator
from explainability.attribution import AttributionTracer
from explainability.reasoning_trace import ReasoningTrace

class ExplainabilityEngine:
    @staticmethod
    def create_explanation(
        query: str,
        is_valid: bool,
        rag_results: List[Dict[str, any]],
        memories: List[str]
    ) -> Dict[str, any]:
        """
        Synthesizes confidence estimation, document attribution, and reasoning traces
        into a single meta payload.
        """
        # 1. Estimate Confidence
        confidence_val = ConfidenceEstimator.estimate(rag_results, memories, is_valid)

        # 2. Trace Citations
        citations = AttributionTracer.trace(rag_results)

        # 3. Log Reasoning chain
        reasoning_log = ReasoningTrace.generate_log(
            query=query,
            has_rag=len(rag_results) > 0,
            has_memories=len(memories) > 0,
            is_valid=is_valid
        )

        return {
            "confidence_score": f"{int(confidence_val * 100)}%",
            "reason_for_answer": reasoning_log,
            "sources_used": citations,
            "memories_used": memories,
            "prompt_summary": f"User query: '{query}' | RAG chunks: {len(rag_results)} | Long-term memory facts: {len(memories)}"
        }
