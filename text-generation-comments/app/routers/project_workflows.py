from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import selectinload

from app.comments_db.session import AsyncSessionLocal
from app.models.workflow_models import ProjectDB, WorkflowDB, ReviewDB, ProjectUserDB, WorkflowStepDB
from app.models.workflow_schemas import ProjectResponse, ProjectDetailResponse, WorkflowResponse, ReviewResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["Project Workflow"]
)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# --- Project Endpoints ---
@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB))
    return result.scalars().all()

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    # Use selectinload to eagerly fetch users
    result = await db.execute(
        select(ProjectDB)
        .options(selectinload(ProjectDB.users))
        .where(ProjectDB.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

# --- Workflow Endpoints ---
@router.get("/projects/{project_id}/workflows", response_model=List[WorkflowResponse])
async def list_project_workflows(project_id: int, db: AsyncSession = Depends(get_db)):
    # Eager load steps
    result = await db.execute(
        select(WorkflowDB)
        .options(selectinload(WorkflowDB.steps))
        .where(WorkflowDB.project_id == project_id)
    )
    workflows = result.scalars().all()
    
    return workflows

# --- Review Endpoints ---
@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review_detail(review_id: int, db: AsyncSession = Depends(get_db)):
    # Eager load actions
    result = await db.execute(
        select(ReviewDB)
        .options(selectinload(ReviewDB.actions))
        .where(ReviewDB.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Enrich with Names (Separate queries for now, could be joins)
    # Note: If we returned a composite object, we'd need a different schema structure.
    # For now, let's manually fetch names and attach to a dict or modified object
    
    resp = ReviewResponse.model_validate(review)
    
    p_res = await db.execute(select(ProjectDB).where(ProjectDB.id == review.project_id))
    w_res = await db.execute(select(WorkflowDB).where(WorkflowDB.id == review.workflow_id))
    
    resp.project_name = p_res.scalar_one().name
    resp.workflow_name = w_res.scalar_one().name
    
    return resp

# --- New Phase 3: Real Persistence Endpoints ---

# 1. Project User Management
from app.models.workflow_schemas import ProjectUserCreate, WorkflowCreate, ReviewCreate, ReviewStatusUpdate

@router.post("/projects/{project_id}/users", response_model=ProjectDetailResponse)
async def assign_project_user(project_id: int, user_data: ProjectUserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user already exists in project
    existing = await db.execute(
        select(ProjectUserDB)
        .where(ProjectUserDB.project_id == project_id, ProjectUserDB.user_id == user_data.user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already assigned to project")

    new_user = ProjectUserDB(
        project_id=project_id,
        user_id=user_data.user_id,
        user_name=user_data.user_name,
        role=user_data.role,        status="Active"
    )
    db.add(new_user)
    await db.commit()
    
    # Return updated project
    return await get_project(project_id, db)

@router.get("/users")
async def list_all_system_users():
    # Mock global user list for dropdown (In real app, fetch from User Service)
    return [
        {"id": "u_arch_01", "name": "Alice Architect", "role": "Architect"},
        {"id": "u_struct_01", "name": "Bob Structural", "role": "Structural Engineer"},
        {"id": "u_mep_01", "name": "Charlie MEP", "role": "MEP Lead"},
        {"id": "u_pm_01", "name": "David Manager", "role": "Project Manager"},
    ]


# 2. Workflow Builder
@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    # Create Workflow
    db_wf = WorkflowDB(
        project_id=workflow.project_id,
        name=workflow.name,
        category=workflow.category,
        approval_type=workflow.approval_type,
        total_steps=workflow.total_steps,
        status="Active"
    )
    db.add(db_wf)
    await db.flush() # Get ID

    # Create Steps
    for step in workflow.steps:
        db_step = WorkflowStepDB(
            workflow_id=db_wf.id,
            step_number=step.step_number,
            step_name=step.step_name,
            required_role=step.required_role,
            time_allowed_days=step.time_allowed_days,
            auto_approval_days=step.auto_approval_days,
            step_color=step.step_color
        )
        db.add(db_step)
    
    await db.commit()
    await db.refresh(db_wf)
    
    # Reload with steps
    result = await db.execute(
        select(WorkflowDB).options(selectinload(WorkflowDB.steps)).where(WorkflowDB.id == db_wf.id)
    )
    return result.scalar_one()


# 3. Review Lifecycle
from datetime import datetime
from app.models.workflow_models import ReviewActionDB

@router.post("/reviews", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    # Create Review
    db_review = ReviewDB(
        code=review.code,
        name=review.name,
        project_id=review.project_id,
        workflow_id=review.workflow_id,
        current_step=1,
        status="In Review",
        description=review.description,
        priority=review.priority,
        start_date=review.start_date or datetime.utcnow(),
        due_date=review.due_date
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    
    # Return detail logic re-use? For now return basic, frontend will fetch detail
    return await get_review_detail(db_review.id, db)

@router.put("/reviews/{review_id}/status", response_model=ReviewResponse)
async def update_review_status(review_id: int, update: ReviewStatusUpdate, db: AsyncSession = Depends(get_db)):
    review = await db.execute(select(ReviewDB).where(ReviewDB.id == review_id))
    review = review.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Fetch Workflow to check max steps
    wf = await db.execute(select(WorkflowDB).where(WorkflowDB.id == review.workflow_id))
    wf = wf.scalar_one()
    
    # Verify Step integrity
    if update.step_number != review.current_step:
         raise HTTPException(status_code=400, detail="Action step mismatch")

    # Record Action
    action = ReviewActionDB(
        review_id=review.id,
        step_number=review.current_step,
        actor_name=update.actor_name,
        action=update.action,
        timestamp=datetime.utcnow()
    )
    db.add(action)

    # State Machine Logic
    if update.action == "SUBMIT":
        if review.current_step < wf.total_steps:
            review.current_step += 1
        else:
            review.status = "Approved"
            
    elif update.action == "REVISE":
        # Go back to step 1 or previous? Simple logic: Go back 1 step (min 1)
        if review.current_step > 1:
            review.current_step -= 1
        review.status = "Revised"

    elif update.action == "REJECT":
        review.status = "Rejected"

    await db.commit()
    return await get_review_detail(review_id, db)
