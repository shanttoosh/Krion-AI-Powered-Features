from app.comments_db.session import AsyncSessionLocal
from app.comments_db.models import ReviewCommentDB
from app.models.review_comment_schemas import ReviewCommentRequest


async def add_review_comment(request: ReviewCommentRequest):
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
