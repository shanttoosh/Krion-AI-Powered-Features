# app/models/feedback_schemas.py

from pydantic import BaseModel
from typing import Optional


class FeedbackRequest(BaseModel):
    suggestion_id: int
    is_helpful: Optional[bool] = None  # 👍 / 👎
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str
