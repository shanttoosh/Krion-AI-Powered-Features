from pydantic import BaseModel
from typing import Optional, Literal

class ReviewCommentRequest(BaseModel):
    review_id: int
    workflow_step: int

    user_name: str
    status: Literal["submit", "revise", "reject"]
    text: str

    parent_id: Optional[int] = None
