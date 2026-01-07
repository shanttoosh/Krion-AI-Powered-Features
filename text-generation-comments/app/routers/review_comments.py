from fastapi import APIRouter, HTTPException
from app.models.review_comment_schemas import ReviewCommentRequest
from app.services.review_comment_service import add_review_comment

router = APIRouter(prefix="/api/v1/review-comments", tags=["Review Comments"])


@router.post("/add")
async def add_comment(request: ReviewCommentRequest):
    try:
        await add_review_comment(request)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
