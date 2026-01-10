import os
import subprocess

def preprocess_audio(
    raw_audio_path: str,
    output_dir: str
) -> str:
    """
    Speech-optimized preprocessing for Whisper
    Returns path to cleaned WAV
    """

    if not os.path.exists(raw_audio_path):
        raise FileNotFoundError(f"Audio not found: {raw_audio_path}")

    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "clean_audio.wav")

    command = [
        "ffmpeg",
        "-y",
        "-i", raw_audio_path,
        "-ac", "1",
        "-ar", "16000",
        "-af", "highpass=f=80,lowpass=f=7600,volume=1.2",
        output_path
    ]

    subprocess.run(command, check=True)
    return output_path
