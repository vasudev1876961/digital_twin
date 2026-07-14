import os
from pathlib import Path
import chromadb
from app.config import Config
from rag.loaders.pdf_loader import PDFLoader
from rag.loaders.text_loader import TextLoader
from rag.chunking.text_chunker import TextChunker
from rag.embedding.vectorizer import Vectorizer
from rag.retrieval.vector_retriever import VectorRetriever
from utils.logger import get_logger

logger = get_logger("rag_pipeline")

class RAGPipeline:
    """
    RAG Pipeline orchestrator utilizing loaders, chunking, vectorizers, and retrievers.
    """
    def __init__(self):
        self.chroma_path = Config.CHROMA_DB_PATH
        self.collection_name = "digital_twin_knowledge"
        self._client = None
        self._collection = None
        self._retriever = None

    def _init_chroma(self):
        if self._client is not None:
            return
        try:
            logger.info(f"Initializing ChromaDB client at: {self.chroma_path}")
            self._client = chromadb.PersistentClient(path=self.chroma_path)
            self._collection = self._client.get_or_create_collection(self.collection_name)
            self._retriever = VectorRetriever(self._collection)
            logger.info("ChromaDB initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise e

    def ingest_directory(self, force_reindex: bool = False):
        self._init_chroma()
        
        if not force_reindex and self._collection.count() > 0:
            logger.info("ChromaDB collection already contains vectors. Skipping ingestion.")
            return

        logger.info("Starting document ingestion process...")

        documents_to_add = []
        embeddings_to_add = []
        metadatas_to_add = []
        ids_to_add = []

        chunk_count = 0
        categories = ["resume", "projects", "certificates", "notes", "linkedin"]

        for cat in categories:
            cat_dir = Config.DOCUMENTS_DIR / cat
            if not cat_dir.exists():
                continue
            
            for file_path in cat_dir.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext not in [".txt", ".md", ".pdf"]:
                        continue

                    # Select appropriate loader
                    text = ""
                    if ext in [".txt", ".md"]:
                        text = TextLoader.load(file_path)
                    elif ext == ".pdf":
                        text = PDFLoader.load(file_path)

                    if not text:
                        continue

                    # Chunk using TextChunker
                    chunks = TextChunker.chunk(text, chunk_size=500, overlap=100)
                    logger.info(f"Generated {len(chunks)} chunks for {file_path.name}")

                    if chunks:
                        embeddings = Vectorizer.get_embeddings(chunks)
                        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                            chunk_id = f"{cat}_{file_path.name}_chunk_{idx}"
                            documents_to_add.append(chunk)
                            embeddings_to_add.append(emb)
                            metadatas_to_add.append({
                                "source": file_path.name,
                                "category": cat,
                                "path": str(file_path.relative_to(Config.DOCUMENTS_DIR))
                            })
                            ids_to_add.append(chunk_id)
                            chunk_count += 1

        # Add to collection
        if documents_to_add:
            try:
                self._collection.add(
                    documents=documents_to_add,
                    embeddings=embeddings_to_add,
                    metadatas=metadatas_to_add,
                    ids=ids_to_add
                )
                logger.info(f"Successfully indexed {chunk_count} chunks in ChromaDB.")
            except Exception as e:
                logger.error(f"Failed to add vectors to ChromaDB: {str(e)}")

    def retrieve(self, query: str, limit: int = 3) -> list:
        self._init_chroma()
        if self._retriever is None:
            return []
        return self._retriever.retrieve(query, limit)
