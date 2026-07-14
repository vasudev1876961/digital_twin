import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from app.config import Config
from app.dependencies import get_stt, get_tts
from utils.audio_utils import convert_to_wav
from utils.logger import get_logger

logger = get_logger("routes_audio")

router = APIRouter(prefix="/audio", tags=["audio"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    stt_model = Depends(get_stt)
):
    """
    Receives an audio file, converts it, and transcribes it using Whisper.
    """
    temp_dir = Config.VOICE_SAMPLES_DIR / "raw"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid concurrency conflicts
    unique_id = uuid.uuid4().hex
    temp_input_path = temp_dir / f"uploaded_{unique_id}_{file.filename}"
    temp_wav_path = temp_dir / f"processed_{unique_id}.wav"

    try:
        # Save uploaded file
        with open(temp_input_path, "wb") as buffer:
            shutil_write(file.file, buffer)

        # Convert to 16kHz WAV mono
        logger.info(f"Converting upload to 16kHz mono WAV: {temp_input_path}")
        conversion_ok = convert_to_wav(temp_input_path, temp_wav_path)
        if not conversion_ok:
            raise HTTPException(status_code=400, detail="Failed to parse or convert audio file format.")

        # Transcribe
        transcription = stt_model.transcribe(str(temp_wav_path))

        return {
            "text": transcription,
            "filename": file.filename
        }

    except Exception as e:
        logger.error(f"Transcribe endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")

    finally:
        # Clean up temp upload files
        if temp_input_path.exists():
            os.remove(temp_input_path)
        if temp_wav_path.exists():
            os.remove(temp_wav_path)

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    tts_model = Depends(get_tts)
):
    """
    Synthesizes speech from text and returns the path/url to the audio file.
    """
    try:
        output_dir = Config.VOICE_SAMPLES_DIR / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"speech_{uuid.uuid4().hex}.wav"
        output_path = output_dir / filename

        success = tts_model.synthesize(text, str(output_path))
        if not success:
            raise HTTPException(status_code=500, detail="Text-to-Speech synthesis failed.")

        return {
            "status": "success",
            "filename": filename,
            "audio_url": f"/audio/download/{filename}"
        }

    except Exception as e:
        logger.error(f"Synthesize endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
def download_audio(filename: str):
    """
    Download/stream generated speech WAV files.
    """
    file_path = Config.VOICE_SAMPLES_DIR / "processed" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=filename
    )

def shutil_write(src, dst):
    import shutil
    shutil.copyfileobj(src, dst)
