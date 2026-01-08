"""
Pydantic models for comment rephrasing API.
Supports Quillbot-style text generation and rephrasing.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class ReviewStatus(str, Enum):
    """Review status options that determine the tone of generated comments."""
    SUBMIT = "submit"
    REJECT = "reject"
    REVISE = "revise"


class WorkflowContext(BaseModel):
    """Optional context about the workflow for better generation."""
    workflow_name: Optional[str] = Field(None, description="Name of the workflow")
    step_name: Optional[str] = Field(None, description="Current step name")
    project_type: Optional[str] = Field(None, description="Type of project (construction, infrastructure, etc.)")
    entity_type: Optional[str] = Field(None, description="Entity being reviewed (document, drawing, etc.)")


class CommentRephraseRequest(BaseModel):
    """Request model for comment rephrasing."""
    input: str = Field(
        ..., 
        description="User's short input text (2-5 words typically)",
        min_length=1,
        max_length=500
    )
    status: ReviewStatus = Field(
        ..., 
        description="Review status - determines the tone of generated suggestions"
    )
    context: Optional[WorkflowContext] = Field(
        None, 
        description="Optional workflow context for better suggestions"
    )
    num_suggestions: int = Field(
        default=3, 
        ge=1, 
        le=5,
        description="Number of alternative suggestions to generate (1-5)"
    )
    # NEW: Thread history for context-aware rephrasing
    thread_history: Optional[List[Dict]] = Field(
        None,
        description="Previous comments in thread for context-aware AI rephrasing"
    )
    parent_comment_id: Optional[int] = Field(
        None,
        description="ID of parent comment if replying to a thread"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "input": "noted will fix",
                "status": "revise",
                "thread_history": [
                    {"user_name": "Senior Engineer", "status": "reject", "text": "BIM column model contains errors. Please correct the dimensions."}
                ],
                "parent_comment_id": 1,
                "num_suggestions": 3
            }
        }


class CommentSuggestion(BaseModel):
    """A single rephrased comment suggestion."""
    text: str = Field(..., description="The rephrased comment text")
    style: str = Field(..., description="Style of this suggestion (formal, concise, friendly)")
    confidence: float = Field(
        default=0.9, 
        ge=0.0, 
        le=1.0,
        description="Confidence score for this suggestion"
    )


class CorrectionsInfo(BaseModel):
    """Information about corrections made to the original input."""
    spelling_corrections: int = Field(default=0, description="Number of spelling corrections made")
    grammar_corrections: int = Field(default=0, description="Number of grammar corrections made")
    terms_expanded: List[str] = Field(
        default_factory=list, 
        description="Construction terms that were expanded (e.g., 'BIM' -> 'Building Information Model')"
    )


class CommentRephraseResponse(BaseModel):
    """Response model for comment rephrasing."""
    success: bool = Field(..., description="Whether rephrasing was successful")
    suggestions: List[CommentSuggestion] = Field(
        default_factory=list, 
        description="List of rephrased comment suggestions"
    )
    corrections: CorrectionsInfo = Field(
        default_factory=CorrectionsInfo,
        description="Information about corrections made"
    )
    original_input: str = Field(..., description="The original user input")
    input_type: str = Field(
        default="expand", 
        description="Type of processing applied: expand, correct, or polish"
    )
    error: Optional[str] = Field(None, description="Error message if rephrasing failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "suggestions": [
                    {
                        "text": "The reinforcement bar spacing does not comply with the approved structural drawings. Please revise and resubmit.",
                        "style": "formal",
                        "confidence": 0.95
                    },
                    {
                        "text": "Rebar spacing is incorrect per specifications. Correction required.",
                        "style": "concise",
                        "confidence": 0.90
                    }
                ],
                "corrections": {
                    "spelling_corrections": 0,
                    "grammar_corrections": 0,
                    "terms_expanded": ["rebar -> reinforcement bar"]
                },
                "original_input": "rebar spacing wrong",
                "input_type": "expand"
            }
        }
