import chromadb
from rag.embedding.vectorizer import Vectorizer
from utils.logger import get_logger

logger = get_logger("vector_retriever")

class VectorRetriever:
    def __init__(self, collection):
        self.collection = collection

    def retrieve(self, query: str, limit: int = 3) -> list:
        if self.collection is None or self.collection.count() == 0:
            return []

        try:
            query_emb = Vectorizer.get_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=limit
            )

            retrieved = []
            if results and results.get("documents"):
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0] if "distances" in results else [0.0] * len(documents)

                for doc, meta, dist in zip(documents, metadatas, distances):
                    score = 1.0 / (1.0 + dist)
                    retrieved.append({
                        "text": doc,
                        "source": meta.get("source", "Unknown"),
                        "category": meta.get("category", "General"),
                        "path": meta.get("path", ""),
                        "score": round(score, 3)
                    })
            return retrieved
        except Exception as e:
            logger.error(f"Vector retriever failed: {str(e)}")
            return []
