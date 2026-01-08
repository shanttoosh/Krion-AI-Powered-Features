"""
FastAPI application entry point for Comment Rephrasing Service.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



# -------------------------------------------------
# CREATE APP FIRST (NO ROUTER IMPORTS YET)
# -------------------------------------------------
app = FastAPI(
    title="Comment Rephrasing Service",
    description="""
    Microservice for expanding and rephrasing short comments into professional construction-domain sentences.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

print("🚀 FastAPI app created")

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🧩 Middleware loaded")

# -------------------------------------------------
# ROUTERS (IMPORT AFTER APP + MIDDLEWARE)
# -------------------------------------------------
from app.routers.rephrase import router as rephrase_router
from app.routers.feedback import router as feedback_router
from app.routers import review_comments

app.include_router(review_comments.router)
app.include_router(rephrase_router)
app.include_router(feedback_router)
from app.routers import project_workflows
app.include_router(project_workflows.router)

print("✅ Routers registered")

# -------------------------------------------------
# STATIC FILES
# -------------------------------------------------
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api-info")
async def api_info():
    return {
        "service": "Comment Rephrasing Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/rephrase-health"
    }

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
