"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


class EntityType(str, Enum):
    """Supported entity types for description generation."""
    ISSUE = "issue"
    REVIEW = "review"
    RFA = "rfa"


class GenerationMode(str, Enum):
    """Available generation modes."""
    TEMPLATE = "template"
    AI = "ai"


class ReviewFields(BaseModel):
    """Fields for Review entity."""
    name: str = Field(..., description="Review name (required)")
    start_date: str = Field(..., description="Start date (required)")
    due_date: str = Field(..., description="Due date (required)")
    workflow: str = Field(..., description="Workflow name (required)")
    priority: str = Field(..., description="Priority level (required)")
    
    # Optional fields
    parent_review: Optional[str] = Field(None, description="Parent review name")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    actual_cost: Optional[float] = Field(None, description="Actual cost")
    checklist: Optional[List[str]] = Field(None, description="Checklist items")


class RFAFields(BaseModel):
    """Fields for RFA (Request for Action) entity."""
    name: str = Field(..., description="RFA name (required)")
    request_date: str = Field(..., description="Request date (required)")
    due_date: str = Field(..., description="Due date (required)")
    workflow: str = Field(..., description="Workflow name (required)")
    priority: str = Field(..., description="Priority level (required)")
    
    # Optional fields
    checklist: Optional[List[str]] = Field(None, description="Checklist items")


class IssueFields(BaseModel):
    """Fields for Issue entity."""
    name: str = Field(..., description="Issue name (required)")
    issue_type: str = Field(..., description="Type of issue (required)")
    placement: str = Field(..., description="Placement/location detail (required)")
    location: str = Field(..., description="Location (required)")
    root_cause: str = Field(..., description="Root cause (required)")
    start_date: str = Field(..., description="Start date (required)")
    due_date: str = Field(..., description="Due date (required)")
    
    # Optional fields
    workflow: Optional[str] = Field(None, description="Workflow name")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    actual_cost: Optional[float] = Field(None, description="Actual cost")


from typing import Union

class GenerationRequest(BaseModel):
    """Request model for description generation with strict field validation."""
    entity_type: EntityType = Field(..., description="Type of entity")
    generation_mode: GenerationMode = Field(
        default=GenerationMode.TEMPLATE,
        description="Generation method: template or ai"
    )
    fields: Union[ReviewFields, RFAFields, IssueFields] = Field(..., description="Entity-specific fields")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "review",
                "generation_mode": "template",
                "fields": {
                    "name": "Phase 1 Inspection",
                    "start_date": "2026-01-05",
                    "due_date": "2026-01-15",
                    "workflow": "Approval Workflow",
                    "priority": "High",
                    "estimated_cost": 50000,
                    "actual_cost": 45000,
                    "checklist": ["Safety Check", "Quality Review"]
                }
            }
        }


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    mode_requested: str = Field(..., description="Generation mode requested by user")
    mode_used: str = Field(..., description="Actual mode used (may differ if fallback occurred)")
    fallback_used: bool = Field(default=False, description="Whether fallback to template was triggered")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback if applicable")
    provider: Optional[str] = Field(None, description="AI provider used (groq, openai, gemini)")
    latency_ms: float = Field(..., description="Generation latency in milliseconds")


class GenerationResponse(BaseModel):
    """Response model for description generation."""
    success: bool = Field(..., description="Whether generation was successful")
    generated_description: str = Field(..., description="The generated description")
    generation_mode: str = Field(..., description="Mode used for generation")
    editable: bool = Field(default=True, description="Whether user can edit the description")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    metadata: Optional[GenerationMetadata] = Field(None, description="Generation metadata for debugging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generated_description": "The High priority review 'Phase 1 Inspection' is scheduled from Jan 5, 2026 to Jan 15, 2026, following the Approval Workflow.",
                "generation_mode": "template",
                "editable": True,
                "metadata": {
                    "mode_requested": "ai",
                    "mode_used": "template",
                    "fallback_used": True,
                    "fallback_reason": "AI timeout after 10s",
                    "provider": "groq",
                    "latency_ms": 10250.5
                }
            }
        }

