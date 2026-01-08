import asyncio
import sys
import os
from sqlalchemy import select

# Fix Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.comments_db.session import AsyncSessionLocal
from app.models.workflow_models import ProjectDB, ProjectUserDB, WorkflowDB, WorkflowStepDB, ReviewDB, ReviewActionDB
from app.comments_db.tables import create_tables

async def seed_data():
    print("🌱 Starting Seed Data Process...")
    
    # Ensure tables exist
    create_tables()

    async with AsyncSessionLocal() as session:
        # 1. Clear existing data (optional, for clean start)
        # await session.execute(delete(ReviewActionDB))
        # await session.execute(delete(ReviewDB))
        # await session.execute(delete(WorkflowStepDB))
        # await session.execute(delete(WorkflowDB))
        # await session.execute(delete(ProjectUserDB))
        # await session.execute(delete(ProjectDB))
        # await session.commit()
        
        # 2. Check if data exists
        result = await session.execute(select(ProjectDB).where(ProjectDB.code == "PRJ-001"))
        if result.scalar_one_or_none():
            print("⚠️ Sample data already exists. Skipping.")
            return

        # 3. Create Projects
        project1 = ProjectDB(
            code="PRJ-001", 
            name="Skyline Tower", 
            status="In Progress", 
            location="New York, NY",
            design_type="Architectural",
            owner="Krion Inc"
        )
        project2 = ProjectDB(
            code="PRJ-002", 
            name="Riverside Mall", 
            status="Open",
            location="London, UK",
            design_type="MEP",
            owner="Global Retail"
        )
        session.add_all([project1, project2])
        await session.flush() # to get IDs

        # 4. Create Users
        users = [
            ProjectUserDB(project_id=project1.id, user_id="u1", user_name="Senior Engineer", role="Approver"),
            ProjectUserDB(project_id=project1.id, user_id="u2", user_name="Junior Modeler", role="Designer"),
            ProjectUserDB(project_id=project1.id, user_id="u3", user_name="Chief Architect", role="D-Contract"),
            # Project 2 users
            ProjectUserDB(project_id=project2.id, user_id="u4", user_name="MEP Lead", role="Approver"),
        ]
        session.add_all(users)
        
        # 5. Create Workflows
        wf1 = WorkflowDB(
            project_id=project1.id,
            name="3-Step Structural Approval",
            category="Structural",
            approval_type="3 Step",
            total_steps=3
        )
        session.add(wf1)
        await session.flush()
        
        # 6. Workflow Steps
        steps = [
            WorkflowStepDB(workflow_id=wf1.id, step_number=1, step_name="Initial Review", required_role="Designer", time_allowed_days=2),
            WorkflowStepDB(workflow_id=wf1.id, step_number=2, step_name="Technical Check", required_role="Approver", time_allowed_days=3),
            WorkflowStepDB(workflow_id=wf1.id, step_number=3, step_name="Final Sign-off", required_role="D-Contract", time_allowed_days=1),
        ]
        session.add_all(steps)
        
        # 7. Create Reviews (Instances of workflows)
        review1 = ReviewDB(
            code="RVW-1001",
            name="Column Grid Review",
            project_id=project1.id,
            workflow_id=wf1.id,
            current_step=2, # Currently at step 2
            status="In Review",
            description="Reviewing the main structural column grids for Tower A.",
            priority="High"
        )
        session.add(review1)
        
        await session.commit()
        print("✅ Seed Data Inserted Successfully!")
        print(f"   - Created Project: {project1.name} (ID: {project1.id})")
        print(f"   - Created Workflow: {wf1.name}")
        print(f"   - Created Review: {review1.name} (Current Step: {review1.current_step})")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_data())
