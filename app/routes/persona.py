import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.config import Config
from app.dependencies import get_persona_engine
from utils.logger import get_logger

logger = get_logger("routes_persona")

router = APIRouter(prefix="/persona", tags=["persona"])

class CommunicationStyle(BaseModel):
    vocabulary: str
    technical_depth: str
    humor_level: str
    greeting_style: str
    formality: str
    sentence_length: str
    frequently_used_phrases: List[str]

class PersonaProfile(BaseModel):
    name: str
    communication_style: CommunicationStyle
    interests: List[str]
    values: List[str]

class SwitchPersonaRequest(BaseModel):
    profile_name: str

@router.get("")
def get_persona(persona_engine = Depends(get_persona_engine)):
    try:
        # Reload profile data to make sure we return fresh disk state
        persona_engine.persona_data = persona_engine._load_persona_profile()
        return persona_engine.persona_data
    except Exception as e:
        logger.error(f"Failed to get persona profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
def update_persona(profile: PersonaProfile, persona_engine = Depends(get_persona_engine)):
    try:
        # Convert schema to dict
        profile_dict = profile.model_dump()
        
        # Write to JSON file
        with open(persona_engine.profile_path, "w") as f:
            json.dump(profile_dict, f, indent=4)
            
        persona_engine.persona_data = profile_dict
        logger.info(f"Updated persona profile '{persona_engine.persona_name}' at: {persona_engine.profile_path}")
        return {"status": "success", "message": f"Successfully updated persona '{persona_engine.persona_name}'."}
    except Exception as e:
        logger.error(f"Failed to update persona profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_personas():
    try:
        profiles_dir = Path(__file__).parent.parent.parent / "personality" / "personality_profiles"
        profiles = []
        if profiles_dir.exists():
            for f in profiles_dir.glob("*.json"):
                profiles.append(f.stem)
        if not profiles:
            profiles = ["vasu"]
        return {"profiles": profiles, "active": Config.PERSONA_PROFILE}
    except Exception as e:
        logger.error(f"Failed to list persona profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch")
def switch_persona(request: SwitchPersonaRequest):
    try:
        profile_name = request.profile_name.strip().lower()
        if not profile_name:
            raise HTTPException(status_code=400, detail="Profile name cannot be empty.")
            
        # Switch the active persona profile name in config
        Config.PERSONA_PROFILE = profile_name
        
        # Clear the singleton cache in app.dependencies
        import app.dependencies
        app.dependencies._persona_engine = None
        
        logger.info(f"Switched active persona profile to: {profile_name}")
        return {"status": "success", "message": f"Switched active persona profile to '{profile_name}'."}
    except Exception as e:
        logger.error(f"Failed to switch persona profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
