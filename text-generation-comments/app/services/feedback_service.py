from app.comments_db.models import CommentFeedbackDB
from app.comments_db.session import AsyncSessionLocal
from typing import Optional

async def save_feedback(
    suggestion_id: int,
    is_helpful: Optional[bool],
    comment: Optional[str] = None
):
    async with AsyncSessionLocal() as db:
        feedback = CommentFeedbackDB(
            suggestion_id=suggestion_id,
            is_helpful=is_helpful,
            comment=comment
        )
        db.add(feedback)
        await db.commit()
