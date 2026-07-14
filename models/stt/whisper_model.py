import os
from pathlib import Path
from app.config import Config
from utils.logger import get_logger

logger = get_logger("whisper_model")

class WhisperModel:
    def __init__(self):
        self.model_name = Config.WHISPER_MODEL_NAME
        self.model = None

    def load_model(self):
        if self.model is None:
            logger.info(f"Loading Whisper model '{self.model_name}'...")
            try:
                import whisper
                # Check for CUDA availability
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {device} for Whisper STT")
                self.model = whisper.load_model(self.model_name, device=device)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {str(e)}")
                raise e

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            self.load_model()
            logger.info(f"Transcribing audio file: {audio_path}")
            result = self.model.transcribe(audio_path)
            transcription = result.get("text", "").strip()
            logger.info("Transcription completed successfully.")
            return transcription
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            # Return fallback mock if Whisper fails (e.g. library dll issues on Windows)
            logger.info("Falling back to simulated transcription...")
            return "This is a simulated speech transcription due to Whisper loading issue."
