import subprocess
import os
import uuid
import wave

def get_audio_duration(path: str) -> float:
    try:
        with wave.open(path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


def preprocess_audio(input_path: str):
    """
    Converts audio to:
    - mono
    - 16kHz
    - WAV (Whisper required)
    """

    output_path = input_path.replace(".webm", "_clean.wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-vn",
        output_path
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    duration = get_audio_duration(output_path)

    return output_path, duration
