from pathlib import Path
from app.config import Config

class VoiceCloningConfig:
    @staticmethod
    def get_cloning_params() -> dict:
        return {
            "speaker_reference": str(Path(Config.XTTS_SPEAKER_REF)),
            "language": "en",
            "model_identifier": "tts_models/multilingual/multi-dataset/xtts_v2"
        }
