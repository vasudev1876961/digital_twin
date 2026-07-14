class ConfidenceEstimator:
    @staticmethod
    def estimate(rag_results: list, memories: list, is_valid: bool) -> float:
        if not is_valid:
            return 0.30
        
        # Start base score
        score = 0.70
        
        # Boost if we have precise RAG chunks
        if rag_results:
            max_score = max([r.get("score", 0.0) for r in rag_results])
            score += (max_score * 0.15)

        # Boost if we have SQLite memories
        if memories:
            score += 0.10

        return min(round(score, 2), 1.0)
