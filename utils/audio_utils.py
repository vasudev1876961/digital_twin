import os
import numpy as np
import soundfile as sf
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("audio_utils")

try:
    from pydub import AudioSegment
except ImportError:
    logger.warning("pydub not installed. Some audio conversions may fail.")

def convert_to_wav(input_path: Path, output_path: Path, target_sr: int = 16000) -> bool:
    """
    Convert any audio file to a standard WAV format (16kHz, mono, 16-bit)
    needed by Whisper and XTTS.
    """
    try:
        if not input_path.exists():
            logger.error(f"Input audio file does not exist: {input_path}")
            return False

        # Load file
        ext = input_path.suffix.lower()
        if ext == ".wav":
            data, sr = sf.read(str(input_path))
            # Convert multi-channel to mono
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            # Resample if necessary
            if sr != target_sr:
                # Basic resampling placeholder using numpy or librosa if available
                # In typical production, pydub or scipy is preferred
                logger.info(f"Resampling WAV from {sr}Hz to {target_sr}Hz")
                # Using pydub for reliable conversion
                sound = AudioSegment.from_wav(str(input_path))
                sound = sound.set_frame_rate(target_sr).set_channels(1)
                sound.export(str(output_path), format="wav")
            else:
                sf.write(str(output_path), data, target_sr)
            return True
        else:
            # Use pydub for mp3, m4a, ogg, webm etc.
            format_name = ext.replace(".", "")
            if format_name == "m4a":
                format_name = "mp4" # pydub processes m4a as mp4
            
            logger.info(f"Converting {ext} to WAV using pydub")
            sound = AudioSegment.from_file(str(input_path), format=format_name)
            sound = sound.set_frame_rate(target_sr).set_channels(1)
            sound.export(str(output_path), format="wav")
            return True

    except Exception as e:
        logger.error(f"Audio conversion failed: {str(e)}")
        return False

def clean_audio(input_path: Path, output_path: Path) -> bool:
    """
    Applies noise reduction/silence stripping. (Placeholder wrapper)
    """
    try:
        # For now, copy file as a placeholder.
        # Future enhancements: apply Spectral Subtraction or gate.
        data, sr = sf.read(str(input_path))
        sf.write(str(output_path), data, sr)
        return True
    except Exception as e:
        logger.error(f"Audio cleaning failed: {str(e)}")
        return False
