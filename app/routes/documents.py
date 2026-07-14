import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from app.config import Config
from app.dependencies import get_rag_pipeline
from utils.logger import get_logger

logger = get_logger("routes_documents")

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    category: str, 
    file: UploadFile = File(...),
    rag_pipeline = Depends(get_rag_pipeline)
):
    valid_categories = ["resume", "projects", "certificates", "notes", "linkedin"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )

    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in [".txt", ".md", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only .txt, .md, and .pdf are allowed."
        )

    try:
        # Save file to respective directory
        target_dir = Config.DOCUMENTS_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / file.filename
        with open(target_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Uploaded file saved to: {target_file}")

        # Trigger RAG ingestion
        logger.info("Triggering RAG database update...")
        rag_pipeline.ingest_directory(force_reindex=True)

        return {
            "status": "success",
            "message": f"Successfully uploaded and indexed {file.filename} in ChromaDB.",
            "file_path": str(target_file.relative_to(Config.BASE_DIR))
        }

    except Exception as e:
        logger.error(f"Failed to upload document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving or indexing file: {str(e)}")

@router.get("/list")
def list_documents():
    """
    Lists all files present in the documents folders.
    """
    try:
        categories = ["resume", "projects", "certificates", "notes", "linkedin"]
        doc_list = []

        for cat in categories:
            cat_dir = Config.DOCUMENTS_DIR / cat
            if cat_dir.exists():
                for file_path in cat_dir.rglob("*"):
                    if file_path.is_file():
                        doc_list.append({
                            "name": file_path.name,
                            "category": cat,
                            "size_bytes": file_path.stat().st_size,
                            "path": str(file_path.relative_to(Config.DOCUMENTS_DIR))
                        })

        return {"documents": doc_list}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex")
def trigger_reindex(rag_pipeline = Depends(get_rag_pipeline)):
    """
    Manually triggers indexing of all files in documents/ directory.
    """
    try:
        rag_pipeline.ingest_directory(force_reindex=True)
        return {"status": "success", "message": "Re-indexing completed successfully."}
    except Exception as e:
        logger.error(f"Manual reindex failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
