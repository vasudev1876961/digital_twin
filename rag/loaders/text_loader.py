from pathlib import Path
from utils.logger import get_logger

logger = get_logger("text_loader")

class TextLoader:
    @staticmethod
    def load(file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path.name}: {str(e)}")
            return ""
