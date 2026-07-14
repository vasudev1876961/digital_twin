class AttributionTracer:
    @staticmethod
    def trace(rag_results: list) -> list:
        citations = []
        for r in rag_results:
            citations.append({
                "source_file": r.get("source", "Unknown"),
                "category": r.get("category", "General"),
                "relevance_score": r.get("score", 0.0),
                "preview_text": r.get("text", "")[:120] + "..."
            })
        return citations
