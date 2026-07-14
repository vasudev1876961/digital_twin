from pathlib import Path
from utils.logger import get_logger

logger = get_logger("pdf_loader")

class PDFLoader:
    @staticmethod
    def load(file_path: Path) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for idx, page in enumerate(reader.pages):
                content = page.extract_text()
                if content:
                    text += content + "\n"
            return text
        except ImportError:
            logger.warning("pypdf is not installed. PDF parsing will be skipped.")
            return ""
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path.name}: {str(e)}")
            return ""
