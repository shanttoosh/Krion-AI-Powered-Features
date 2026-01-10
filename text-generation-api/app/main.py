"""
FastAPI application entry point for Text Generation API
(with Whisper Speech-to-Text support).
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import generation, whisper
from app.config import settings
from app.models.whisper_model import get_whisper_model

# ------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "extra": %(extra)s}',
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class ExtraFilter(logging.Filter):
    """Ensure `extra` field always exists in logs."""
    def filter(self, record):
        if not hasattr(record, "extra"):
            record.extra = "{}"
        else:
            import json
            record.extra = json.dumps(getattr(record, "extra", {}))
        return True


for handler in logging.root.handlers:
    handler.addFilter(ExtraFilter())

logger = logging.getLogger(__name__)
logger.info("Text Generation API starting up")


# ------------------------------------------------------
# FastAPI App
# ------------------------------------------------------

app = FastAPI(
    title="Text Generation API",
    description="""
    API for generating descriptions for Review, RFA, and Issue entities,
    with additional Speech-to-Text support using Whisper.

    ## Features
    - Template-based description generation
    - AI-powered description generation (OpenAI / Groq / Gemini)
    - Automatic fallback handling
    - Speech-to-English transcription (Whisper)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ------------------------------------------------------
# CORS Configuration
# ------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------
# Routers
# ------------------------------------------------------

# Existing text generation APIs
app.include_router(generation.router)

# Whisper speech-to-text APIs
app.include_router(whisper.router)


# ------------------------------------------------------
# Root & Health
# ------------------------------------------------------


@app.on_event("startup")
def warmup_whisper():
    logger.info("Warming up Whisper model...")
    get_whisper_model()
    logger.info("Whisper model loaded and ready")

@app.get("/")
async def root():
    return {
        "service": "Text Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "features": [
            "Text Generation (Template / AI)",
            "Speech-to-Text (Whisper)"
        ]
    }


# ------------------------------------------------------
# Local Development Entry
# ------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
