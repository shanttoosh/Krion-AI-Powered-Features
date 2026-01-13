from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile, os, time

from app.models.whisper_model import get_whisper_model
from app.services.preprocess import preprocess_audio
from app.models.llm_translate import translate

router = APIRouter(
    prefix="/api/v1/whisper",
    tags=["Whisper"]
)

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    total_start = time.perf_counter()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        raw_path = tmp.name

    clean_path = None

    try:
        # 🔹 Preprocess
        preprocess_start = time.perf_counter()
        clean_path, duration = preprocess_audio(raw_path)
        preprocess_time = round(time.perf_counter() - preprocess_start, 3)

        if duration < 1.5:
            return {"success": False, "warning": "Audio too short"}

        # 🔹 Whisper
        whisper = get_whisper_model()
        whisper_start = time.perf_counter()
        result = whisper.transcribe(clean_path)
        whisper_time = round(time.perf_counter() - whisper_start, 3)

        text = result.get("text", "").strip()
        language = result.get("language", "unknown")
        confidence = round(result.get("confidence", 0.0), 3)

        if not text:
            return {"success": False, "warning": "No speech detected"}

        if confidence < 0.5:
            return {
                "success": False,
                "detected_language": language,
                "speech_text": text,
                "confidence": confidence,
                "warning": "Low confidence audio"
            }

        # 🔹 Translation rule (IMPORTANT)
        if language == "en":
            english_text = text
            translation_time = 0.0
        else:
            english_text, translation_time = translate(text)

        return {
            "success": True,
            "detected_language": language,
            "speech_text": text,
            "english_text": english_text,
            "confidence": confidence,
            "timing": {
                "preprocess_seconds": preprocess_time,
                "whisper_seconds": whisper_time,
                "translation_seconds": translation_time,
                "total_seconds": round(time.perf_counter() - total_start, 3)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for p in [raw_path, clean_path]:
            if p and os.path.exists(p):
                os.remove(p)
