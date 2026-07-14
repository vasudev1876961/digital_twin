import os
from utils.logger import get_logger

logger = get_logger("embedding_model")

class EmbeddingModel:
    def __init__(self):
        self.model_name = "BAAI/bge-large-en-v1.5"
        self.fallback_model_name = "all-MiniLM-L6-v2"
        self.model = None
        self._initialized = False

    def load_model(self):
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading embedding model '{self.model_name}' on device {device}...")
            # Try to load primary model
            self.model = SentenceTransformer(self.model_name, device=device)
            self._initialized = True
            logger.info("Primary embedding model loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load primary embedding model '{self.model_name}': {str(e)}")
            logger.info(f"Attempting to load fallback model '{self.fallback_model_name}'...")
            try:
                from sentence_transformers import SentenceTransformer
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = SentenceTransformer(self.fallback_model_name, device=device)
                self._initialized = True
                logger.info("Fallback embedding model loaded successfully.")
            except Exception as ex:
                logger.error(f"Failed to load fallback embedding model: {str(ex)}")
                self._initialized = False

    def get_embedding(self, text: str):
        """
        Generate embedding for a single text.
        """
        self.load_model()
        if self._initialized and self.model is not None:
            # sentence-transformers encode returns a numpy array
            return self.model.encode(text).tolist()
        else:
            # Returns a mock embedding (dimension 384) if load fails entirely
            logger.warning("Embedding model not loaded. Returning dummy embedding.")
            import random
            return [random.uniform(-0.1, 0.1) for _ in range(384)]

    def get_embeddings(self, texts: list):
        """
        Generate embeddings for a list of texts.
        """
        self.load_model()
        if self._initialized and self.model is not None:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        else:
            logger.warning("Embedding model not loaded. Returning dummy embeddings list.")
            return [self.get_embedding(t) for t in texts]
