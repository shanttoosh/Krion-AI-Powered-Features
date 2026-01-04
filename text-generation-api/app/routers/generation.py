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
    - **fields**: Dictionary of field values for the entity
    
    Returns a generated description that the user can edit.
    """
    try:
        # Validate entity type
        valid_types = ["issue", "review", "rfa"]
        if request.entity_type.value not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity_type. Must be one of: {valid_types}"
            )
        
        # Generate description
        description, mode_used = await description_generator.generate(
            entity_type=request.entity_type.value,
            generation_mode=request.generation_mode,
            fields=request.fields
        )
        
        return GenerationResponse(
            success=True,
            generated_description=description,
            generation_mode=mode_used,
            editable=True
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
