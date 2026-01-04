"""
API routes for comment rephrasing (Quillbot-style).
"""
from fastapi import APIRouter, HTTPException
from app.models.rephrase_schemas import CommentRephraseRequest, CommentRephraseResponse
from app.services.comment_rephraser import comment_rephraser

router = APIRouter(prefix="/api/v1", tags=["Comment Rephrasing"])


@router.post("/rephrase-comment", response_model=CommentRephraseResponse)
async def rephrase_comment(request: CommentRephraseRequest) -> CommentRephraseResponse:
    """
    Rephrase a short comment into professional, grammatically correct alternatives.
    
    This endpoint provides Quillbot-style text generation and rephrasing for
    workflow review comments in construction project management.
    
    - **input**: User's short input text (e.g., "rebar spacing wrong")
    - **status**: Review status (submit, reject, revise) - determines tone
    - **context**: Optional workflow context for better suggestions
    - **num_suggestions**: Number of alternatives to generate (1-5, default 3)
    
    Returns 2-3 professional alternatives with different styles (formal, concise, friendly).
    
    **Example Use Cases:**
    - User types "wrong dimensions" with status "reject"
    - API returns: "The submitted drawings contain dimensional errors that do not conform to specifications. Please revise and resubmit."
    """
    try:
        # Validate input is not empty
        if not request.input.strip():
            raise HTTPException(
                status_code=400,
                detail="Input text cannot be empty"
            )
        
        # Rephrase the comment
        response = await comment_rephraser.rephrase(request)
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return CommentRephraseResponse(
            success=False,
            suggestions=[],
            original_input=request.input,
            input_type="expand",
            error=str(e)
        )


@router.get("/rephrase-health")
async def rephrase_health_check():
    """Health check endpoint for comment rephrasing service."""
    return {
        "status": "healthy",
        "service": "comment-rephrasing",
        "features": ["expansion", "grammar_correction", "tone_based_generation"]
    }
