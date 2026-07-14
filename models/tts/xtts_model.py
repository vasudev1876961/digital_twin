import os
from pathlib import Path
from app.config import Config
from utils.logger import get_logger

logger = get_logger("xtts_model")

class XTTSModel:
    def __init__(self):
        self.speaker_ref_wav = Path(Config.XTTS_SPEAKER_REF)
        self.tts_engine = None
        self.mode = "gTTS" # Defaults to gTTS fallback, will check for XTTS

    def load_model(self):
        """
        Attempts to load local XTTS-v2 model. If it fails or is not installed,
        falls back to gTTS.
        """
        if self.tts_engine is not None:
            return

        try:
            # Check if reference speaker wav exists, otherwise warn
            if not self.speaker_ref_wav.exists():
                logger.warning(f"XTTS reference audio not found at: {self.speaker_ref_wav}. Will use default voice fallback.")
            
            logger.info("Checking for local Coqui TTS installation...")
            import torch
            from TTS.api import TTS
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Initializing XTTS-v2 model on device: {device}...")
            
            # This downloads and initializes XTTS-v2 (warning: first run downloads ~2GB)
            self.tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            self.mode = "XTTS"
            logger.info("XTTS-v2 model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load local XTTS-v2 model ({str(e)}). Falling back to gTTS.")
            self.mode = "gTTS"

    def synthesize(self, text: str, output_path: str) -> bool:
        """
        Synthesize text into a WAV file.
        """
        try:
            self.load_model()
            logger.info(f"Synthesizing voice (Mode: {self.mode}) for text: '{text[:30]}...'")

            if self.mode == "XTTS" and self.tts_engine is not None and self.speaker_ref_wav.exists():
                # Run XTTS-v2 voice cloning
                self.tts_engine.tts_to_file(
                    text=text,
                    speaker_wav=str(self.speaker_ref_wav),
                    language="en",
                    file_path=output_path
                )
                logger.info(f"XTTS audio generated successfully at: {output_path}")
                return True
            else:
                # Fallback to gTTS (Google Text-to-Speech)
                from gtts import gTTS
                # gTTS generates mp3, we save to mp3 and convert to wav or let gtts write directly
                # To keep it simple, we can save to mp3 and convert to wav using pydub, or just write mp3
                temp_mp3 = output_path.replace(".wav", ".mp3")
                tts_obj = gTTS(text=text, lang="en", slow=False)
                tts_obj.save(temp_mp3)

                # Convert MP3 to WAV using our audio helper
                from utils.audio_utils import convert_to_wav
                success = convert_to_wav(Path(temp_mp3), Path(output_path))
                
                # Cleanup temp mp3
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)

                if success:
                    logger.info(f"gTTS audio generated and converted to WAV at: {output_path}")
                    return True
                else:
                    logger.error("Failed to convert gTTS output to WAV.")
                    return False

        except Exception as e:
            logger.error(f"Voice synthesis failed: {str(e)}")
            return False
