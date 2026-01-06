from fastapi import APIRouter, HTTPException
from app.models.feedback_schemas import FeedbackRequest
from app.services.feedback_service import save_feedback

router = APIRouter(prefix="/api/v1", tags=["Feedback"])

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        await save_feedback(
            suggestion_id=request.suggestion_id,
            is_helpful=request.is_helpful
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
