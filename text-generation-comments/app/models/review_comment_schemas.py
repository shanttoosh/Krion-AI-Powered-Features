from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime


class ReviewCommentRequest(BaseModel):
    """Request to add a new review comment."""
    review_id: int
    workflow_step: int
    user_name: str
    status: Literal["submit", "revise", "reject"]
    text: str
    parent_id: Optional[int] = None


class ReviewCommentResponse(BaseModel):
    """Single comment response."""
    id: int
    review_id: int
    workflow_step: int
    user_name: str
    status: str
    text: str
    parent_id: Optional[int] = None
    created_at: datetime
    replies: List["ReviewCommentResponse"] = []

    class Config:
        from_attributes = True


class ReviewCommentsListResponse(BaseModel):
    """Response for listing comments with threading."""
    success: bool
    review_id: int
    total_comments: int
    comments: List[ReviewCommentResponse]  # Top-level comments (threads)


class CommentThreadContext(BaseModel):
    """Context for AI rephrasing - includes previous comments in thread."""
    review_id: int
    workflow_step: int
    thread_history: List[dict]  # Previous comments in the thread
    current_status: Literal["submit", "revise", "reject"]
