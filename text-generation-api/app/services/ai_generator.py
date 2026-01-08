"""
AI-powered description generator.
Supports OpenAI, Groq, and Google Gemini - NO FALLBACK for testing.
"""
from typing import Dict, Any
import asyncio
from app.config import settings
from app.services.template_generator import template_generator


class AIGenerator:
    """Generates descriptions using AI (OpenAI, Groq, or Gemini)."""
    
    def __init__(self):
        """Initialize AI clients based on configuration."""
        self.openai_client = None
        self.groq_client = None
        self.gemini_model = None
        self._initialized = False
    
    def _initialize_clients(self):
        """Initialize AI provider clients (lazy initialization)."""
        if self._initialized:
            return
        
        self._initialized = True
        
        print(f"🔧 AI Provider from .env: '{settings.ai_provider}'")
        print(f"🔧 Groq Key present: {bool(settings.groq_api_key)}")
        print(f"🔧 OpenAI Key present: {bool(settings.openai_api_key)}")
        
        if settings.ai_provider == "openai" and settings.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI: {e}")
        
        elif settings.ai_provider == "groq" and settings.groq_api_key:
            try:
                from openai import OpenAI
                self.groq_client = OpenAI(
                    api_key=settings.groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                print("✅ Groq client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Groq: {e}")
        
        elif settings.ai_provider == "gemini" and settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                model_name = "models/gemini-pro-latest"
                self.gemini_model = genai.GenerativeModel(model_name)
                print(f"✅ Gemini client initialized with model: {model_name}")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
        else:
            print(f"⚠️ No matching provider found for: {settings.ai_provider}")
    
    def _build_prompt(self, entity_type: str, fields: Dict[str, Any]) -> str:
        """Build the AI prompt for description generation."""
        fields_text = "\n".join([f"- {key}: {value}" for key, value in fields.items() if value])
        
        entity_name = "Review" if entity_type == "review" else "Request for Approval" if entity_type == "rfa" else "Issue"
        
        prompt = f"""You are a professional document description writer for a construction/project management system.

Generate a concise, professional description for a {entity_name} with these details:
{fields_text}

Requirements:
- Keep it under 100 words
- Use professional, formal tone
- Include all provided key information naturally
- Make it easy to read and understand
- Write in paragraph form (no bullet points)
- Do not include any placeholders or brackets

Generate only the description text, nothing else."""
        
        return prompt
    
    
    async def generate_with_metadata(self, entity_type: str, fields: Dict[str, Any]) -> tuple:
        """
        Generate description using AI with metadata.
        Returns: (description, metadata_dict)
        """
        # Lazy initialization
        self._initialize_clients()
        
        metadata = {
            "fallback_used": False,
            "fallback_reason": None,
            "provider": None
        }
        
        try:
            prompt = self._build_prompt(entity_type, fields)
            
            if settings.ai_provider == "openai" and self.openai_client:
                print("🚀 Using OpenAI...")
                description = await self._generate_openai(prompt)
                metadata["provider"] = "openai"
                return description, metadata
                
            elif settings.ai_provider == "groq" and self.groq_client:
                print("🚀 Using Groq...")
                description = await self._generate_groq(prompt)
                metadata["provider"] = "groq"
                return description, metadata
                
            elif settings.ai_provider == "gemini" and self.gemini_model:
                print("🚀 Using Gemini...")
                description = await self._generate_gemini(prompt)
                metadata["provider"] = "gemini"
                return description, metadata
            else:
                # No AI configured
                print("⚠️ AI not configured, falling back to template")
                metadata["fallback_used"] = True
                metadata["fallback_reason"] = "AI provider not configured"
                return template_generator.generate(entity_type, fields), metadata
        
        except Exception as e:
            # AI failed
            print(f"⚠️ AI failed: {e}. Falling back to template.")
            metadata["fallback_used"] = True
            metadata["fallback_reason"] = str(e)
            return template_generator.generate(entity_type, fields), metadata
    
    async def generate(self, entity_type: str, fields: Dict[str, Any]) -> str:
        """
        Generate description using AI.
        Falls back to template if AI fails.
        """
        description, _ = await self.generate_with_metadata(entity_type, fields)
        return description
    
    async def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional technical writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
        )
        return response.choices[0].message.content.strip()
    
    async def _generate_groq(self, prompt: str) -> str:
        """Generate using Groq API (OpenAI-compatible)."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional technical writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
        )
        return response.choices[0].message.content.strip()
    
    async def _generate_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini API."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini_model.generate_content(prompt)
        )
        return response.text.strip()


# Singleton instance
ai_generator = AIGenerator()
