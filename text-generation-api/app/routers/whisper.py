from fastapi import APIRouter, UploadFile, File
import os
import uuid

from app.models.whisper_model import get_whisper_model
from app.services.preprocess import preprocess_audio

router = APIRouter(
    prefix="/api/v1/whisper",
    tags=["Speech-to-Text"]
)

RAW_DIR = "audio/raw"
CLEAN_DIR = "audio/clean"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    raw_path = os.path.join(RAW_DIR, f"{uuid.uuid4()}_{file.filename}")

    with open(raw_path, "wb") as f:
        f.write(await file.read())

    try:
        # ✅ Preprocess FIRST
        clean_path = preprocess_audio(raw_path, CLEAN_DIR)

        # ✅ Then Whisper
        model = get_whisper_model()
        result = model.transcribe_to_english(clean_path)

        return {
            "success": True,
            **result
        }

    finally:
        # Cleanup
        if os.path.exists(raw_path):
            os.remove(raw_path)

