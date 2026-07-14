import google.generativeai as genai
from app.config import Config
from utils.logger import get_logger

logger = get_logger("gemini_model")

class GeminiModel:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self._model = None
        self._initialized = False

    def _init_client(self):
        if self._initialized:
            return
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set in environment. Gemini client will run in mock mode.")
            return

        try:
            logger.info("Initializing Gemini API client...")
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            logger.info("Gemini API client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {str(e)}")
            self._initialized = False

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate response content using Gemini API.
        """
        self._init_client()

        if not self._initialized or self._model is None:
            logger.warning("Gemini client not initialized. Returning mock response.")
            return "Hello! I am Vasu's digital twin. Please set GEMINI_API_KEY in the .env file to enable real conversations."

        try:
            logger.info(f"Generating content for prompt with len: {len(prompt)}")
            
            # Using system instructions if provided
            if system_instruction:
                # In modern google-generativeai, system_instruction can be passed during model creation or generation config.
                # A very safe way to run this without API variation errors is to pre-create a model with system_instruction
                # or prepend it directly to the prompt or use the generation config.
                # Creating a custom model instance with system instruction is the cleanest way:
                local_model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
                response = local_model.generate_content(prompt)
            else:
                response = self._model.generate_content(prompt)

            text = response.text.strip()
            return text
        except Exception as e:
            logger.error(f"Gemini API content generation failed: {str(e)}")
            return f"Error from Gemini API: {str(e)}. Please check your API key and connection."
