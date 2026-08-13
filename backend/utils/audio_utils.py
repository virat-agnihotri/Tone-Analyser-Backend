import os
import uuid
from pathlib import Path
import librosa
import soundfile as sf

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def generate_filename(original_filename: str) -> str:
    # Strip directory components to prevent path traversal
    basename = os.path.basename(original_filename)
    extension = Path(basename).suffix.lower() or ".wav"
    return f"{uuid.uuid4()}{extension}"


def save_audio(file_bytes: bytes, filename: str) -> str:
    safe_filename = generate_filename(filename)
    path = UPLOAD_DIR / safe_filename

    with open(path, "wb") as f:
        f.write(file_bytes)

    return str(path)


def get_audio_duration(audio_path: str) -> float:
    try:
        return float(librosa.get_duration(path=audio_path))
    except Exception:
        return 0.0


def convert_to_wav(audio_path: str) -> str:
    audio_path_obj = Path(audio_path)
    output_path = str(audio_path_obj.with_name(f"{audio_path_obj.stem}_converted.wav"))

    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        if len(y) == 0:
            raise ValueError("Audio stream contains no samples.")
        sf.write(output_path, y, sr, format="WAV")
        return output_path
    except Exception as e:
        # If conversion fails but file exists, return original if wav
        if audio_path.lower().endswith(".wav"):
            return audio_path
        raise RuntimeError(f"Audio conversion failed: {str(e)}")


def split_audio(audio_path: str, chunk_length: int = 30):
    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        chunk_size = chunk_length * sr
        chunks = []
        for i in range(0, len(y), chunk_size):
            chunk = y[i:i + chunk_size]
            if len(chunk) > 0:
                chunks.append((i / sr, chunk))
        return chunks
    except Exception:
        return []