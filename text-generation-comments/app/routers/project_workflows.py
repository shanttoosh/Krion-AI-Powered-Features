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
