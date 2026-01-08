from fastapi import APIRouter, HTTPException, Query
from app.models.review_comment_schemas import (
    ReviewCommentRequest,
    ReviewCommentsListResponse,
    ReviewCommentResponse
)
from app.services.review_comment_service import (
    add_review_comment,
    get_comments_by_review,
    get_comment_thread,
    get_comments_by_workflow_step
)

router = APIRouter(prefix="/api/v1/review-comments", tags=["Review Comments"])


@router.post("/add")
async def add_comment(request: ReviewCommentRequest):
    """
    Add a new review comment.
    
    - **review_id**: ID of the review
    - **workflow_step**: Step number (1-7)
    - **user_name**: Name of the reviewer
    - **status**: submit / revise / reject
    - **text**: Comment text
    - **parent_id**: Optional - ID of parent comment for threading
    """
    try:
        comment_id = await add_review_comment(request)
        return {"success": True, "comment_id": comment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{review_id}")
async def list_comments(review_id: int):
    """
    Get all comments for a review, organized as threaded structure.
    
    Returns top-level comments with nested replies.
    """
    try:
        comments = await get_comments_by_review(review_id)
        return {
            "success": True,
            "review_id": review_id,
            "total_comments": len(comments),
            "comments": comments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thread/{comment_id}")
async def get_thread(comment_id: int):
    """
    Get the full thread history for a comment (for AI context).
    
    Returns the comment and all its ancestors in chronological order.
    Useful for context-aware AI rephrasing.
    """
    try:
        thread = await get_comment_thread(comment_id)
        return {
            "success": True,
            "thread": thread,
            "total_in_thread": len(thread)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-step/{review_id}/{workflow_step}")
async def list_by_step(review_id: int, workflow_step: int):
    """
    Get all comments for a specific workflow step.
    
    - **review_id**: ID of the review
    - **workflow_step**: Step number (1-7)
    """
    try:
        comments = await get_comments_by_workflow_step(review_id, workflow_step)
        return {
            "success": True,
            "review_id": review_id,
            "workflow_step": workflow_step,
            "comments": comments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
