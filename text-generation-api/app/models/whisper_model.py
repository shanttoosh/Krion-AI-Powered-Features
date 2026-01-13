import time
import whisper
from app.config import settings

class WhisperModel:
    def __init__(self):
        self.model = whisper.load_model(settings.whisper_model_size)

    def transcribe(self, audio_path: str):
        start = time.time()

        result = self.model.transcribe(
            audio_path,
            task="transcribe",
            temperature=0.0,
            beam_size=5,
            best_of=5,
            condition_on_previous_text=False
        )

        segments = result.get("segments", [])
        avg_logprob = sum(
            s.get("avg_logprob", -10.0) for s in segments
        ) / max(len(segments), 1)

        confidence = max(0.0, min(1.0, (avg_logprob + 2) / 2))

        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "confidence": round(confidence, 3),
            "whisper_seconds": round(time.time() - start, 3)
        }

_whisper = None

def get_whisper_model():
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel()
    return _whisper
