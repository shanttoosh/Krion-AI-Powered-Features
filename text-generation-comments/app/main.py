"""
FastAPI application entry point for Comment Rephrasing Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import rephrase
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="Comment Rephrasing Service",
    description="""
    Microservice for expanding and rephrasing short comments into professional construction-domain sentences.
    
    ## Features
    - **Tone-based Generation**: Adapts to Submit/Reject/Revise status
    - **Construction Knowledge**: Expands terms like 'BIM', 'RFI', 'NCR'
    - **Multi-style Output**: Formal, concise, and friendly alternatives
    - **Spelling & Grammar**: Auto-correction during rephrasing
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rephrase.router)

# Mount frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_root():
    """Serve the frontend application."""
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api-info")
async def api_info():
    """API Information endpoint (moved from root)."""
    return {
        "service": "Comment Rephrasing Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/rephrase-health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
