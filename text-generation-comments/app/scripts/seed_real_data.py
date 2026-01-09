import asyncio
import sys
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import select, delete

# Fix Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.comments_db.session import AsyncSessionLocal
from app.models.workflow_models import ProjectDB, ProjectUserDB, WorkflowDB, WorkflowStepDB, ReviewDB, ReviewActionDB
from app.comments_db.tables import create_tables

PROJECT_NAMES = [
    ("Skyline Tower", "New York, NY", "Architectural"),
    ("Riverfront Mall", "London, UK", "MEP"),
    ("Metro Station Beta", "Berlin, DE", "Structural"),
    ("Oceanic Resort", "Maldives", "Architectural"),
    ("Tech Park Alpha", "San Francisco, CA", "MEP"),
    ("City Hospital", "Toronto, CA", "Structural"),
    ("Grand Stadium", "Melbourne, AU", "Architectural"),
    ("Logistics Hub", "Dubai, UAE", "MEP"),
    ("Solar Power Plant", "Nevada, USA", "Electrical"),
    ("Green Valley Housing", "Austin, TX", "Architectural")
]

ROLES = ["Project Manager", "Architect", "Structural Engineer", "MEP Lead", "Client Rep", "BIM Coordinator"]
WORKFLOW_TYPES = [
    ("Structural Approval", "Structural", ["Initial Check", "Load Analysis", "Final Sign-off"]),
    ("MEP Coordination", "MEP", ["Clash Detection", "System Review"]),
    ("Client Design Review", "Architectural", ["Concept Review", "Material Selection", "Client Approval"]),
    ("Safety Compliance", "Safety", ["Safety Audit", "Regulation Check"])
]

async def seed_real_data():
    print("🌱 Starting REAL Data Seeding (10+ Projects)...")
    
    # Ensure tables exist
    create_tables()

    async with AsyncSessionLocal() as session:
        # 1. Clear existing data
        print("   - Clearing existing data...")
        await session.execute(delete(ReviewActionDB))
        await session.execute(delete(ReviewDB))
        await session.execute(delete(WorkflowStepDB))
        await session.execute(delete(WorkflowDB))
        await session.execute(delete(ProjectUserDB))
        await session.execute(delete(ProjectDB))
        await session.commit()

        projects = []
        users = []
        workflows = []
        workflow_steps = []
        reviews = []

        # 2. Design Projects
        for i, (name, loc, type_) in enumerate(PROJECT_NAMES):
            p = ProjectDB(
                code=f"PRJ-{1000+i}",
                name=name,
                status=random.choice(["Open", "In Progress", "In Progress", "In Progress", "Closed"]),
                start_date=datetime.utcnow() - timedelta(days=random.randint(10, 365)),
                location=loc,
                design_type=type_,
                owner=f"Krion Client {i+1}"
            )
            projects.append(p)
        
        session.add_all(projects)
        await session.flush() # Get IDs

        # 3. Users, Workflows, Reviews
        for p in projects:
            # Users
            p_users = []
            for role in ROLES:
                u = ProjectUserDB(
                    project_id=p.id,
                    user_id=f"u_{p.id}_{role[:3]}",
                    user_name=f"{role} ({p.code})",
                    role=role,
                    status="Active"
                )
                p_users.append(u)
            users.extend(p_users)

            # Workflows
            p_workflows = []
            # Add 2 random workflows per project
            selected_wfs = random.sample(WORKFLOW_TYPES, 2)
            for wf_name, cat, steps_names in selected_wfs:
                wf = WorkflowDB(
                    project_id=p.id,
                    name=wf_name,
                    category=cat,
                    approval_type=f"{len(steps_names)} Step",
                    total_steps=len(steps_names),
                    status="Active"
                )
                p_workflows.append((wf, steps_names)) # Tuple to track steps
            
            # Flush Workflows to get IDs
            session.add_all([x[0] for x in p_workflows])
            await session.flush()

            # Workflow Steps & Reviews
            for wf, step_names in p_workflows:
                # Steps
                for idx, s_name in enumerate(step_names):
                    step = WorkflowStepDB(
                        workflow_id=wf.id,
                        step_number=idx+1,
                        step_name=s_name,
                        required_role=random.choice(ROLES),
                        time_allowed_days=random.randint(2, 7)
                    )
                    workflow_steps.append(step)
                
                # Create 1-3 Reviews per workflow
                for r_idx in range(random.randint(1, 3)):
                    current = random.randint(1, wf.total_steps)
                    review = ReviewDB(
                        code=f"RVW-{wf.id}-{r_idx}",
                        name=f"{wf.category} Review #{r_idx+1}",
                        project_id=p.id,
                        workflow_id=wf.id,
                        current_step=current,
                        status=random.choice(["In Review", "In Review", "Revised", "Approved"]) if current == wf.total_steps else "In Review",
                        description=f"Reviewing deliverables for {wf.name}. Please check compliance.",
                        priority=random.choice(["High", "Medium", "Low"]),
                        start_date=datetime.utcnow(),
                        due_date=datetime.utcnow() + timedelta(days=5)
                    )
                    reviews.append(review)

        session.add_all(users)
        session.add_all(workflow_steps)
        session.add_all(reviews)

        await session.commit()
        print("✅ Seed Real Data Complete!")
        print(f"   - Projects: {len(projects)}")
        print(f"   - Users: {len(users)}")
        print(f"   - Workflows: {len(workflows)} (approx)")
        print(f"   - Reviews: {len(reviews)}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_real_data())
