"""
API routes for description generation.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerationRequest, GenerationResponse
from app.services.generator import description_generator

router = APIRouter(prefix="/api/v1", tags=["Generation"])


@router.post("/generate-description", response_model=GenerationResponse)
async def generate_description(request: GenerationRequest) -> GenerationResponse:
    """
    Generate a description for the specified entity based on provided fields.
    
    - **entity_type**: Type of entity (issue, review, rfa)
    - **generation_mode**: Method to use (template or ai)
    - **fields**: Entity-specific fields (validated by Pydantic)
    
    Returns a generated description with metadata.
    """
    try:
        # Convert Pydantic model to dict for generators
        fields_dict = request.fields.dict() if hasattr(request.fields, 'dict') else request.fields.model_dump()
        
        # Generate description with metadata
        description, mode_used, metadata = await description_generator.generate(
            entity_type=request.entity_type.value,
            generation_mode=request.generation_mode,
            fields=fields_dict
        )
        
        return GenerationResponse(
            success=True,
            generated_description=description,
            generation_mode=mode_used,
            editable=True,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return GenerationResponse(
            success=False,
            generated_description="",
            generation_mode=request.generation_mode.value,
            editable=True,
            error=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "text-generation-api"}
