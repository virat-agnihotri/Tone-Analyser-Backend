import torch
import librosa
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
from config import EMOTION_MODEL, get_hf_token

_processor = None
_model = None

LABEL_MAPPING = {
    "neu": "neutral",
    "hap": "happy",
    "ang": "angry",
    "sad": "sad",
    "fea": "fear",
    "exc": "excited",
    "sur": "surprised",
    "dis": "disgusted",
    "fru": "frustrated",
    "oth": "neutral"
}


import os

def get_emotion_model():
    global _processor, _model
    if _processor is None or _model is None:
        print(f"Loading emotion classification model: {EMOTION_MODEL}")
        is_offline = os.getenv("HF_HUB_OFFLINE", "0") in ("1", "true", "True")

        try:
            _processor = AutoFeatureExtractor.from_pretrained(EMOTION_MODEL, local_files_only=True)
            _model = AutoModelForAudioClassification.from_pretrained(EMOTION_MODEL, local_files_only=True)
            _model.eval()
            print(f"Loaded emotion classification model '{EMOTION_MODEL}' from local cache.")
            return _processor, _model
        except Exception as local_err:
            if is_offline:
                print(
                    "Unable to reach Hugging Face Hub.\n"
                    "This may be a DNS/network problem rather than an authentication problem.\n"
                    "Please verify that huggingface.co can be resolved and reached."
                )
                raise RuntimeError(
                    f"Emotion model '{EMOTION_MODEL}' is not available in local cache and offline mode is active."
                ) from local_err
            print(f"Emotion model '{EMOTION_MODEL}' not cached. Trying online load...")

        try:
            _processor = AutoFeatureExtractor.from_pretrained(EMOTION_MODEL, local_files_only=False)
            _model = AutoModelForAudioClassification.from_pretrained(EMOTION_MODEL, local_files_only=False)
            _model.eval()
            print(f"Successfully downloaded and loaded emotion classification model '{EMOTION_MODEL}'.")
        except Exception as net_err:
            print(
                "Unable to reach Hugging Face Hub.\n"
                "This may be a DNS/network problem rather than an authentication problem.\n"
                "Please verify that huggingface.co can be resolved and reached."
            )
            raise RuntimeError(
                f"Emotion model '{EMOTION_MODEL}' is not cached and Hugging Face (huggingface.co) "
                f"could not be reached: {net_err}"
            ) from net_err

    return _processor, _model


def detect_emotion_from_samples(y, sr: int = 16000) -> dict:
    try:
        if len(y) == 0:
            return {"emotion": "neutral", "confidence": 0.5, "all_scores": {"neutral": 0.5}}

        processor, model = get_emotion_model()
        inputs = processor(y, sampling_rate=sr, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        id2label = model.config.id2label
        all_scores = {LABEL_MAPPING.get(id2label[i].lower(), id2label[i].lower()): float(probs[i]) for i in range(len(probs))}

        top_idx = torch.argmax(probs).item()
        raw_label = id2label[top_idx].lower()
        mapped_label = LABEL_MAPPING.get(raw_label, raw_label)
        confidence = float(probs[top_idx])

        return {
            "emotion": mapped_label,
            "confidence": round(confidence, 4),
            "all_scores": all_scores
        }
    except Exception as e:
        print(f"Warning: Emotion detection error ({e}). Returning fallback.")
        return {"emotion": "neutral", "confidence": 0.5, "all_scores": {"neutral": 0.5}}


def detect_emotion(audio_path: str) -> dict:
    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        return detect_emotion_from_samples(y, sr)
    except Exception as e:
        print(f"Warning: Emotion detection error ({e}). Returning fallback.")
        return {"emotion": "neutral", "confidence": 0.5, "all_scores": {"neutral": 0.5}}


# Alias expected by routers/analysis.py
analyze_emotion = detect_emotion
analyze_emotion_from_samples = detect_emotion_from_samples