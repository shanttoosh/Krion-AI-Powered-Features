import os
import whisper
from app.config import settings

# Ensure FFmpeg is visible
os.environ["PATH"] += os.pathsep + r"C:\Users\Krion\Documents\ffmpeg\bin"


class WhisperVoiceModel:
    def __init__(self):
        self.model = whisper.load_model(settings.whisper_model_size)

    def transcribe_to_english(self, audio_path: str):
        """
        Single-pass translation for speed + confidence filtering
        """

        # -----------------------------
        # Whisper inference (ONE pass)
        # -----------------------------
        result = self.model.transcribe(
            audio_path,
            task="translate",
            temperature=0.0,
            beam_size=5,
            best_of=5,
            no_speech_threshold=0.6,
            logprob_threshold=-1.0,
            compression_ratio_threshold=2.0,
            condition_on_previous_text=False
        )

        # -----------------------------
        # Confidence guard
        # -----------------------------
        segments = result.get("segments", [])

        if segments:
            avg_logprob = sum(
                s.get("avg_logprob", -10.0) for s in segments
            ) / len(segments)
        else:
            avg_logprob = -10.0

        if avg_logprob < -1.2:
            return {
                "detected_language": result.get("language", "unknown"),
                "english_text": "",
                "warning": "Low confidence audio – transcription suppressed"
            }

        # -----------------------------
        # Final output
        # -----------------------------
        return {
            "detected_language": result.get("language", "unknown"),
            "english_text": result["text"].strip()
        }


# -------------------------------------------------
# Lazy-loaded singleton (FastAPI safe)
# -------------------------------------------------
_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperVoiceModel()
    return _whisper_model
