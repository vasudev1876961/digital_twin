import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("recorder")

class VoiceRecorder:
    @staticmethod
    def record(output_path: Path, duration_seconds: int = 5, sample_rate: int = 16000) -> bool:
        """
        Record audio from the microphone and save it as a WAV file.
        (Works locally on Windows systems with soundcard input available)
        """
        try:
            logger.info(f"Recording microphone input for {duration_seconds} seconds...")
            # Capture mono audio
            recording = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.int16
            )
            sd.wait() # Block until finished
            
            # Save recording
            sf.write(str(output_path), recording, sample_rate)
            logger.info(f"Microphone recording saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to record from microphone: {str(e)}")
            return False
        return False
