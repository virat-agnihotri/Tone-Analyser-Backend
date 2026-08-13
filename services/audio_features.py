import librosa
import numpy as np


def _clean_float(val, default=0.0) -> float:
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return default
        return round(f, 4)
    except Exception:
        return default


def extract_audio_features_from_samples(y: np.ndarray, sr: int = 16000) -> dict:
    if len(y) == 0:
        return {
            "duration": 0.0,
            "pitch_mean": 0.0,
            "pitch_std": 0.0,
            "energy_mean": 0.0,
            "energy_std": 0.0,
            "zcr_mean": 0.0,
            "speech_duration": 0.0,
            "speaking_ratio": 0.0,
        }

    total_duration = len(y) / sr

    # RMS Energy
    rms = librosa.feature.rms(y=y)[0]
    energy_mean = _clean_float(np.mean(rms))
    energy_std = _clean_float(np.std(rms))

    # Pitch tracking
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = []

    for frame in range(pitches.shape[1]):
        index = np.argmax(magnitudes[:, frame])
        pitch = pitches[index, frame]
        if pitch > 0:
            pitch_values.append(pitch)

    if pitch_values:
        pitch_mean = _clean_float(np.mean(pitch_values))
        pitch_std = _clean_float(np.std(pitch_values))
    else:
        pitch_mean = 0.0
        pitch_std = 0.0

    # Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = _clean_float(np.mean(zcr))

    # Speech Activity / Silence ratio
    try:
        intervals = librosa.effects.split(y, top_db=30)
        speech_samples = sum(end - start for start, end in intervals)
        speech_duration = speech_samples / sr
    except Exception:
        speech_duration = total_duration

    speaking_ratio = (
        _clean_float(speech_duration / total_duration)
        if total_duration > 0
        else 0.0
    )

    return {
        "duration": _clean_float(total_duration),
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "energy_mean": energy_mean,
        "energy_std": energy_std,
        "zcr_mean": zcr_mean,
        "speech_duration": _clean_float(speech_duration),
        "speaking_ratio": speaking_ratio,
    }


def extract_audio_features(audio_path: str) -> dict:
    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
    except Exception as e:
        raise ValueError(f"Could not load audio file: {str(e)}")

    if len(y) == 0:
        raise ValueError("Audio file is empty.")

    return extract_audio_features_from_samples(y, sr)