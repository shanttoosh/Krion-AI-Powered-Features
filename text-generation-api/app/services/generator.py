"""
Main generator orchestrator.
Routes requests to appropriate generator based on mode.
"""
from typing import Dict, Any, Tuple
from app.models.schemas import GenerationMode
from app.services.template_generator import template_generator
from app.services.ai_generator import ai_generator


class DescriptionGenerator:
    """Orchestrates description generation based on mode."""
    
    async def generate(
        self, 
        entity_type: str, 
        generation_mode: GenerationMode,
        fields: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Generate description based on mode.
        
        Args:
            entity_type: Type of entity (review, rfa, issue)
            generation_mode: Template or AI mode
            fields: Dictionary of field values
            
        Returns:
            Tuple of (generated_description, actual_mode_used)
        """
        if generation_mode == GenerationMode.TEMPLATE:
            description = template_generator.generate(entity_type, fields)
            return description, "template"
        
        elif generation_mode == GenerationMode.AI:
            description = await ai_generator.generate(entity_type, fields)
            # Check if fallback was used (AI may fall back to template)
            return description, "ai"
        
        else:
            # Default to template
            description = template_generator.generate(entity_type, fields)
            return description, "template"


# Singleton instance
description_generator = DescriptionGenerator()
