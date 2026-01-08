"""
Main generator orchestrator with metadata tracking and logging.
Routes requests to appropriate generator based on mode.
"""
import time
import logging
from typing import Dict, Any, Tuple, Optional
from app.models.schemas import GenerationMode, GenerationMetadata
from app.services.template_generator import template_generator
from app.services.ai_generator import ai_generator

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """Orchestrates description generation based on mode."""
    
    async def generate(
        self, 
        entity_type: str, 
        generation_mode: GenerationMode,
        fields: Dict[str, Any]
    ) -> Tuple[str, str, GenerationMetadata]:
        """
        Generate description based on mode with metadata tracking.
        
        Args:
            entity_type: Type of entity (review, rfa, issue)
            generation_mode: Template or AI mode
            fields: Dictionary of field values
            
        Returns:
            Tuple of (generated_description, actual_mode_used, metadata)
        """
        start_time = time.time()
        mode_requested = generation_mode.value
        
        logger.info("Generation started", extra={
            "entity_type": entity_type,
            "mode_requested": mode_requested,
            "has_optional_fields": self._has_optional_fields(fields)
        })
        
        # Default metadata
        metadata = GenerationMetadata(
            mode_requested=mode_requested,
            mode_used=mode_requested,
            fallback_used=False,
            latency_ms=0.0
        )
        
        try:
            if generation_mode == GenerationMode.TEMPLATE:
                description = template_generator.generate(entity_type, fields)
                metadata.mode_used = "template"
                mode_used = "template"
                
            elif generation_mode == GenerationMode.AI:
                # Try AI generation
                description, ai_metadata = await ai_generator.generate_with_metadata(entity_type, fields)
                
                # Check if AI actually worked or fell back
                if ai_metadata.get("fallback_used"):
                    metadata.fallback_used = True
                    metadata.fallback_reason = ai_metadata.get("fallback_reason", "Unknown")
                    metadata.mode_used = "template"
                    mode_used = "template"
                    logger.warning("AI fallback triggered", extra={
                        "reason": metadata.fallback_reason,
                        "entity_type": entity_type
                    })
                else:
                    metadata.mode_used = "ai"
                    metadata.provider = ai_metadata.get("provider")
                    mode_used = "ai"
                    logger.info("AI generation successful", extra={
                        "provider": metadata.provider,
                        "entity_type": entity_type
                    })
            else:
                # Default to template
                description = template_generator.generate(entity_type, fields)
                metadata.mode_used = "template"
                mode_used = "template"
                
        except Exception as e:
            # Fallback to template on any error
            logger.error("Generation failed, using template fallback", extra={
                "error": str(e),
                "entity_type": entity_type
            })
            description = template_generator.generate(entity_type, fields)
            metadata.fallback_used = True
            metadata.fallback_reason = f"Exception: {str(e)}"
            metadata.mode_used = "template"
            mode_used = "template"
        
        # Calculate latency
        metadata.latency_ms = (time.time() - start_time) * 1000
        
        logger.info("Generation completed", extra={
            "entity_type": entity_type,
            "mode_used": metadata.mode_used,
            "fallback_used": metadata.fallback_used,
            "latency_ms": metadata.latency_ms
        })
        
        return description, mode_used, metadata
    
    def _has_optional_fields(self, fields: Dict[str, Any]) -> bool:
        """Check if request has optional fields populated."""
        optional_keys = {'parent_review', 'estimated_cost', 'actual_cost', 'checklist'}
        return any(fields.get(key) is not None for key in optional_keys)


# Singleton instance
description_generator = DescriptionGenerator()
