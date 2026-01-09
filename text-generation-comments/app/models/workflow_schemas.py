from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Project Schemas ---
class ProjectUser(BaseModel):
    user_id: str
    user_name: str
    role: str
    status: str
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    code: str
    name: str
    status: str
    location: Optional[str] = None
    design_type: Optional[str] = None
    owner: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    start_date: datetime
    
    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    users: List[ProjectUser] = []

# --- Workflow Schemas ---
class WorkflowStep(BaseModel):
    step_number: int
    step_name: str
    required_role: Optional[str] = None
    time_allowed_days: int = 1
    auto_approval_days: int = 0
    step_color: str = "#2fb380"
    
    class Config:
        from_attributes = True

class WorkflowBase(BaseModel):
    name: str
    category: str
    approval_type: str = "2 Step Approval"
    total_steps: int = 2

class WorkflowCreate(WorkflowBase):
    project_id: int
    steps: List[WorkflowStep]

class WorkflowResponse(WorkflowBase):
    id: int
    project_id: int
    status: str
    steps: List[WorkflowStep] = []

    class Config:
        from_attributes = True

# --- Review Schemas ---
class ReviewAction(BaseModel):
    step_number: int
    actor_name: str
    action: str
    timestamp: datetime
    comment_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    priority: str = "Medium"
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

class ReviewCreate(ReviewBase):
    project_id: int
    workflow_id: int

class ReviewResponse(ReviewBase):
    id: int
    project_id: int
    workflow_id: int
    current_step: int
    status: str
    
    # Nested data for UI
    project_name: Optional[str] = None # Enriched in service
    workflow_name: Optional[str] = None # Enriched
    actions: List[ReviewAction] = []

    class Config:
        from_attributes = True

# --- Project User Schemas ---
class ProjectUserCreate(BaseModel):
    user_id: str
    user_name: str
    role: str

# --- Review Status Update ---
class ReviewStatusUpdate(BaseModel):
    action: str  # SUBMIT, REVISE, REJECT
    comment: str
    actor_name: str
    step_number: int
