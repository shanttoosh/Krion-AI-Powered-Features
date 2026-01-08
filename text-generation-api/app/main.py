"""
FastAPI application entry point for Text Generation API.
"""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import generation
from app.config import settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "extra": %(extra)s}',
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Custom filter to ensure 'extra' field exists
class ExtraFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'extra'):
            record.extra = '{}'
        else:
            import json
            record.extra = json.dumps(getattr(record, 'extra', {}))
        return True

for handler in logging.root.handlers:
    handler.addFilter(ExtraFilter())

logger = logging.getLogger(__name__)
logger.info("Text Generation API starting up")

# Create FastAPI app
app = FastAPI(
    title="Text Generation API",
    description="""
    API for generating descriptions for Review, RFA, and Issue entities.
    
    ## Features
    - **Template-based generation**: Fast, predictable descriptions using templates
    - **AI-powered generation**: Natural, context-aware descriptions using OpenAI/Gemini
    - **Smart field detection**: Automatically includes optional fields when provided
    - **Fallback mechanism**: AI falls back to template if API fails
    
    ## Supported Entities
    - **Review**: Generate descriptions for project reviews
    - **RFA**: Generate descriptions for Request for Action items
    - **Issue**: Generate descriptions for issues (existing feature extension)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Text Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
