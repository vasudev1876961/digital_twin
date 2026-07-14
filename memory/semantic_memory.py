import chromadb
from app.config import Config
from app.dependencies import get_embeddings
from utils.logger import get_logger

logger = get_logger("semantic_memory")

class SemanticMemory:
    """
    Manages episodic and conceptual semantic memory stored in ChromaDB
    (separate from the general RAG documents collection).
    """
    def __init__(self):
        self.chroma_path = Config.CHROMA_DB_PATH
        self.collection_name = "digital_twin_semantic_memories"
        self._client = None
        self._collection = None

    def _init_db(self):
        if self._client is not None:
            return
        try:
            self._client = chromadb.PersistentClient(path=self.chroma_path)
            self._collection = self._client.get_or_create_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Failed to initialize Chroma semantic memory: {str(e)}")

    def add_memory(self, memory_text: str, tags: dict = None):
        self._init_db()
        if self._collection is None:
            return
        
        try:
            import uuid
            embedder = get_embeddings()
            emb = embedder.get_embedding(memory_text)
            memory_id = f"mem_{uuid.uuid4().hex}"
            self._collection.add(
                documents=[memory_text],
                embeddings=[emb],
                metadatas=[tags or {}],
                ids=[memory_id]
            )
            logger.info("Saved episodic memory to semantic database.")
        except Exception as e:
            logger.error(f"Failed to save episodic memory: {str(e)}")

    def search_memories(self, query: str, limit: int = 2) -> list:
        self._init_db()
        if self._collection is None or self._collection.count() == 0:
            return []
        
        try:
            embedder = get_embeddings()
            emb = embedder.get_embedding(query)
            results = self._collection.query(
                query_embeddings=[emb],
                n_results=limit
            )
            
            memories = []
            if results and results.get("documents"):
                memories = results["documents"][0]
            return memories
        except Exception as e:
            logger.error(f"Failed to search semantic memories: {str(e)}")
            return []
