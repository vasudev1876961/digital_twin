from utils.logger import get_logger

logger = get_logger("qwen_model")

class QwenModel:
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        self.model = None
        self.tokenizer = None
        self._initialized = False

    def load_model(self):
        if self._initialized:
            return

        try:
            logger.info(f"Checking for local GPU/CPU transformers load of {self.model_name}...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading tokenizer and causal LLM {self.model_name} on {device}...")
            
            # Load tokenizer and model (could take a while on CPU, handles lazy instantiation)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto"
            )
            self._initialized = True
            logger.info("Qwen local model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load local Qwen model ({str(e)}). Ensure transformers is installed and hardware has enough RAM/VRAM.")
            self._initialized = False

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate response using Qwen. Falls back to mock or Gemini if local load is not initialized.
        """
        self.load_model()
        
        if not self._initialized or self.model is None or self.tokenizer is None:
            logger.info("Qwen not loaded. Falling back to Gemini or default response.")
            # Standard developer placeholder response for Qwen
            return "Qwen local model placeholder response (not fully initialized). Please set up your local GPU/HuggingFace dependencies to run Qwen locally."

        try:
            device = self.model.device
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response.strip()
        except Exception as e:
            logger.error(f"Local Qwen generation failed: {str(e)}")
            return f"Error generating text from Qwen: {str(e)}"
