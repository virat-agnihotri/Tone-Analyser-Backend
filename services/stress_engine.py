from utils.scoring import emotion_to_score, clamp, stress_level


def calculate_stress(audio_features: dict, emotion_data: dict) -> dict:
    emotion = emotion_data.get("emotion", "neutral") if emotion_data else "neutral"
    emotion_score = emotion_to_score(emotion)

    energy = audio_features.get("energy_mean", 0.0) if audio_features else 0.0
    pitch_std = audio_features.get("pitch_std", 0.0) if audio_features else 0.0
    speaking_ratio = audio_features.get("speaking_ratio", 0.0) if audio_features else 0.0

    # Heuristic metrics scaling
    energy_score = clamp(energy * 1000.0 if energy < 0.1 else energy * 100.0)
    pitch_score = clamp(pitch_std / 2.0)
    speech_score = clamp(speaking_ratio * 100.0)

    score = (
        emotion_score * 0.45 +
        energy_score * 0.20 +
        pitch_score * 0.20 +
        speech_score * 0.15
    )
    score = round(clamp(score), 2)
    level_str = stress_level(score)

    return {
        "score": score,
        "level": level_str,
        "factors": [
            f"Emotion State: {emotion.capitalize()}",
            f"Vocal Energy: {round(energy_score, 2)}",
            f"Pitch Variation: {round(pitch_score, 2)}",
            f"Speech Activity: {round(speech_score, 2)}"
        ]
    }