from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.comments_db.base import Base

class ProjectDB(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="Open")  # Open, In Progress, Closed
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    design_type = Column(String, nullable=True) # e.g. "MEP", "Architectural"
    owner = Column(String, nullable=True)
    
    # Relationships
    workflows = relationship("WorkflowDB", back_populates="project")
    reviews = relationship("ReviewDB", back_populates="project")
    users = relationship("ProjectUserDB", back_populates="project")

class ProjectUserDB(Base):
    __tablename__ = "project_users"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(String, nullable=False) # Simplified for now (just string ID/Name)
    user_name = Column(String, nullable=False)
    role = Column(String, nullable=False) # e.g. "Approver", "Designer"
    status = Column(String, default="Active")
    
    project = relationship("ProjectDB", back_populates="users")

class WorkflowDB(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g. "Process", "Approval"
    approval_type = Column(String, default="2 Step Approval") # Display string
    total_steps = Column(Integer, default=1)
    status = Column(String, default="Active")
    
    project = relationship("ProjectDB", back_populates="workflows")
    steps = relationship("WorkflowStepDB", back_populates="workflow", order_by="WorkflowStepDB.step_number")
    reviews = relationship("ReviewDB", back_populates="workflow")

class WorkflowStepDB(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    step_number = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    time_allowed_days = Column(Integer, default=1)
    auto_approval_days = Column(Integer, default=0)
    step_color = Column(String, default="#2fb380")
    required_role = Column(String, nullable=True) # e.g. "Senior Engineer"
    
    workflow = relationship("WorkflowDB", back_populates="steps")

class ReviewDB(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    
    current_step = Column(Integer, default=1) # 1-based index
    status = Column(String, default="In Review") # In Review, Revised, Rejected, Approved
    
    description = Column(Text, nullable=True)
    priority = Column(String, default="Medium")
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    
    project = relationship("ProjectDB", back_populates="reviews")
    workflow = relationship("WorkflowDB", back_populates="reviews")
    actions = relationship("ReviewActionDB", back_populates="review")

class ReviewActionDB(Base):
    __tablename__ = "review_actions"
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    step_number = Column(Integer, nullable=False)
    actor_name = Column(String, nullable=False)
    action = Column(String, nullable=False) # SUBMIT, REVISE, REJECT
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment_id = Column(Integer, nullable=True) # Link to review_comments table if needed
    
    review = relationship("ReviewDB", back_populates="actions")
