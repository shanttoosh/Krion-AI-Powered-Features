from app.comments_db.session import AsyncSessionLocal
from app.comments_db.models import CommentFeedbackDB
import asyncio

async def test_feedback():
    async with AsyncSessionLocal() as db:
        feedback = CommentFeedbackDB(
            suggestion_id=1,   # must exist in comment_suggestions
            is_helpful=True
        )
        db.add(feedback)
        await db.commit()

    print("✅ Feedback inserted successfully")

asyncio.run(test_feedback())
