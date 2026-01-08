from app.comments_db.session import AsyncSessionLocal
from app.comments_db.models import ReviewCommentDB
from app.models.review_comment_schemas import ReviewCommentRequest, ReviewCommentResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional


async def add_review_comment(request: ReviewCommentRequest) -> int:
    """Add a new review comment and return its ID."""
    async with AsyncSessionLocal() as db:
        comment = ReviewCommentDB(
            review_id=request.review_id,
            workflow_step=request.workflow_step,
            user_name=request.user_name,
            status=request.status,
            text=request.text,
            parent_id=request.parent_id
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment.id


async def get_comments_by_review(review_id: int) -> List[dict]:
    """
    Fetch all comments for a review, organized as threaded structure.
    Returns top-level comments with nested replies.
    """
    async with AsyncSessionLocal() as db:
        # Get all comments for this review
        result = await db.execute(
            select(ReviewCommentDB)
            .where(ReviewCommentDB.review_id == review_id)
            .order_by(ReviewCommentDB.created_at)
        )
        all_comments = result.scalars().all()
        
        # Build threaded structure
        comments_dict = {}
        top_level = []
        
        # First pass: create dict of all comments
        for comment in all_comments:
            comments_dict[comment.id] = {
                "id": comment.id,
                "review_id": comment.review_id,
                "workflow_step": comment.workflow_step,
                "user_name": comment.user_name,
                "status": comment.status,
                "text": comment.text,
                "parent_id": comment.parent_id,
                "created_at": comment.created_at,
                "replies": []
            }
        
        # Second pass: build tree structure
        for comment in all_comments:
            if comment.parent_id is None:
                top_level.append(comments_dict[comment.id])
            else:
                if comment.parent_id in comments_dict:
                    comments_dict[comment.parent_id]["replies"].append(
                        comments_dict[comment.id]
                    )
        
        return top_level


async def get_comment_thread(comment_id: int) -> List[dict]:
    """
    Get a single comment thread - the comment and all its ancestors.
    Useful for AI context when replying.
    """
    async with AsyncSessionLocal() as db:
        thread = []
        current_id = comment_id
        
        while current_id is not None:
            result = await db.execute(
                select(ReviewCommentDB).where(ReviewCommentDB.id == current_id)
            )
            comment = result.scalar_one_or_none()
            
            if comment is None:
                break
            
            thread.append({
                "id": comment.id,
                "user_name": comment.user_name,
                "status": comment.status,
                "text": comment.text,
                "created_at": str(comment.created_at)
            })
            current_id = comment.parent_id
        
        # Reverse to get oldest first (for AI context)
        return list(reversed(thread))


async def get_comments_by_workflow_step(review_id: int, workflow_step: int) -> List[dict]:
    """Get comments for a specific workflow step."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ReviewCommentDB)
            .where(ReviewCommentDB.review_id == review_id)
            .where(ReviewCommentDB.workflow_step == workflow_step)
            .order_by(ReviewCommentDB.created_at)
        )
        comments = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "user_name": c.user_name,
                "status": c.status,
                "text": c.text,
                "parent_id": c.parent_id,
                "created_at": str(c.created_at)
            }
            for c in comments
        ]
