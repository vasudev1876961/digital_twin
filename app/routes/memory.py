from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_memory_manager
from utils.logger import get_logger

logger = get_logger("routes_memory")

router = APIRouter(prefix="/memory", tags=["memory"])

class FactRequest(BaseModel):
    key: str
    value: str

@router.get("")
def list_memories(memory_manager = Depends(get_memory_manager)):
    try:
        facts = memory_manager.long_term.get_all_facts()
        # Seed defaults if database is empty to ensure a good first experience
        if not facts:
            memory_manager._seed_default_facts()
            facts = memory_manager.long_term.get_all_facts()
        formatted_facts = [{"key": k, "value": v} for k, v in facts.items()]
        return {"facts": formatted_facts}
    except Exception as e:
        logger.error(f"Failed to list memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
def add_memory(request: FactRequest, memory_manager = Depends(get_memory_manager)):
    try:
        if not request.key.strip() or not request.value.strip():
            raise HTTPException(status_code=400, detail="Key and value cannot be empty.")
        
        # Clean key to be lowercase and use snake_case
        clean_key = request.key.strip().replace(" ", "_").lower()
        memory_manager.save_fact(clean_key, request.value.strip())
        return {"status": "success", "message": f"Saved fact '{clean_key}' to long-term memory."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to add memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{key}")
def delete_memory(key: str, memory_manager = Depends(get_memory_manager)):
    try:
        facts = memory_manager.long_term.get_all_facts()
        if key not in facts:
            raise HTTPException(status_code=404, detail=f"Fact with key '{key}' not found.")
            
        memory_manager.delete_fact(key)
        return {"status": "success", "message": f"Deleted fact '{key}' from long-term memory."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to delete memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
