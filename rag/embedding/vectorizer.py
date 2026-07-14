from app.dependencies import get_embeddings

class Vectorizer:
    @staticmethod
    def get_embeddings(texts: list) -> list:
        embedder = get_embeddings()
        return embedder.get_embeddings(texts)

    @staticmethod
    def get_embedding(text: str) -> list:
        embedder = get_embeddings()
        return embedder.get_embedding(text)
