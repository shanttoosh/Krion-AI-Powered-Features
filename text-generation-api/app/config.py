"""
Configuration settings for the Text Generation API.
Uses simple environment variables for maximum compatibility.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # AI Provider Configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
        # Generation Settings
        self.default_generation_mode = os.getenv("DEFAULT_GENERATION_MODE", "template")
        self.max_description_length = int(os.getenv("MAX_DESCRIPTION_LENGTH", "500"))
        
        # OpenAI Model Settings
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Gemini Model Settings
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")

        # Whisper (Speech-to-Text) Settings
        self.whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "small") 


settings = Settings()
