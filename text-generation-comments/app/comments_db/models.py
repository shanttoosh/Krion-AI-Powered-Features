from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.comments_db.base import Base


class CommentRequestDB(Base):
    __tablename__ = "comment_requests"

    id = Column(Integer, primary_key=True)
    input_text = Column(String, nullable=False)
    status = Column(String, nullable=False)
    input_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    suggestions = relationship(
        "CommentSuggestionDB",
        back_populates="request",
        cascade="all, delete-orphan"
    )


class CommentSuggestionDB(Base):
    __tablename__ = "comment_suggestions"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("comment_requests.id"), nullable=False)

    text = Column(String, nullable=False)
    style = Column(String, nullable=False)
    confidence = Column(Float)
    provider = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Existing relationship
    request = relationship("CommentRequestDB", back_populates="suggestions")

    # ✅ NEW — feedback relationship
    feedback = relationship(
        "CommentFeedbackDB",
        back_populates="suggestion",
        cascade="all, delete-orphan"
    )

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.comments_db.base import Base


class CommentFeedbackDB(Base):
    __tablename__ = "comment_feedback"

    id = Column(Integer, primary_key=True)
    suggestion_id = Column(Integer, ForeignKey("comment_suggestions.id"), nullable=False)

    is_helpful = Column(Boolean, nullable=True)   # 👍 / 👎
    comment = Column(String, nullable=True)       # ✅ ADD THIS

    created_at = Column(DateTime, default=datetime.utcnow)

    suggestion = relationship("CommentSuggestionDB", back_populates="feedback")


class ReviewCommentDB(Base):
    __tablename__ = "review_comments"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, nullable=False)
    workflow_step = Column(Integer, nullable=False)

    user_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # submit / revise / reject
    text = Column(String, nullable=False)

    parent_id = Column(Integer, ForeignKey("review_comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship(
        "ReviewCommentDB",
        remote_side=[id],
        backref="replies"
    )

