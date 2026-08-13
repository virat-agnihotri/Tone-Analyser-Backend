import os
import librosa
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, pipeline
from config import WHISPER_MODEL

_transcriber = None


def get_transcriber():
    global _transcriber
    if _transcriber is None:
        print(f"Loading speech-to-text model: {WHISPER_MODEL}")
        is_offline_env = os.getenv("HF_HUB_OFFLINE", "0") in ("1", "true", "True")

        # 1. Try loading processor and model from local Hugging Face cache first
        try:
            processor = AutoProcessor.from_pretrained(WHISPER_MODEL, local_files_only=True)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(WHISPER_MODEL, local_files_only=True)
            _transcriber = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor
            )
            print(f"Loaded speech-to-text model from local cache.")
            return _transcriber
        except Exception as local_err:
            if is_offline_env:
                print(
                    "Unable to reach Hugging Face Hub.\n"
                    "This may be a DNS/network problem rather than an authentication problem.\n"
                    "Please verify that huggingface.co can be resolved and reached."
                )
                raise RuntimeError(
                    f"Whisper model '{WHISPER_MODEL}' is not available in local cache and offline mode is active."
                ) from local_err
            print(f"Whisper model '{WHISPER_MODEL}' not fully cached locally. Attempting online load...")

        # 2. Try online load if not cached
        try:
            processor = AutoProcessor.from_pretrained(WHISPER_MODEL, local_files_only=False)
            model = AutoModelForSpeechSeq2Seq.from_pretrained(WHISPER_MODEL, local_files_only=False)
            _transcriber = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor
            )
            print(f"Successfully downloaded and loaded speech-to-text model '{WHISPER_MODEL}'.")
        except Exception as net_err:
            print(
                "Unable to reach Hugging Face Hub.\n"
                "This may be a DNS/network problem rather than an authentication problem.\n"
                "Please verify that huggingface.co can be resolved and reached."
            )
            raise RuntimeError(
                f"Speech-to-text model '{WHISPER_MODEL}' is not cached and Hugging Face (huggingface.co) "
                f"could not be reached: {net_err}"
            ) from net_err

    return _transcriber


def transcribe_audio(audio_path: str) -> dict:
    try:
        transcriber = get_transcriber()

        # Load raw audio via librosa to bypass external ffmpeg dependency
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        if len(y) == 0:
            return {"text": "[Audio file is empty]", "segments": []}

        # Pass in-memory numpy array directly to Hugging Face pipeline
        audio_input = {"raw": y, "sampling_rate": sr}
        result = transcriber(audio_input, return_timestamps=True)

        text = result.get("text", "").strip()
        chunks = result.get("chunks", [])
        segments = []

        for chunk in chunks:
            timestamp = chunk.get("timestamp")
            start = timestamp[0] if (timestamp and len(timestamp) > 0) else None
            end = timestamp[1] if (timestamp and len(timestamp) > 1) else None
            segments.append({
                "start": start,
                "end": end,
                "text": chunk.get("text", "").strip()
            })

        if not text:
            text = "[Driver speech recorded - background engine noise]"

        return {
            "text": text,
            "segments": segments
        }
    except Exception as e:
        print(f"Warning: Whisper transcription error ({e}). Returning fallback.")
        return {
            "text": "[Audio transcription fallback]",
            "segments": []
        }