from pathlib import Path
from utils.logger import get_logger

logger = get_logger("player")

class VoicePlayer:
    @staticmethod
    def play(audio_path: Path) -> bool:
        """
        Play a WAV file locally. (For testing audio output locally)
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            logger.info(f"Playing audio clip: {audio_path.name}")
            data, fs = sf.read(str(audio_path), dtype='float32')
            sd.play(data, fs)
            sd.wait()
            logger.info("Playback completed.")
            return True
        except Exception as e:
            logger.error(f"Playback failed: {str(e)}")
            return False
