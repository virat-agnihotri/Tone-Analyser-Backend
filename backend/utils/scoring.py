def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    if value is None or not isinstance(value, (int, float)):
        return minimum
    return max(minimum, min(maximum, float(value)))


def normalize_score(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.0
    score = ((value - min_value) / (max_value - min_value)) * 100.0
    return clamp(score)


def emotion_to_score(emotion: str) -> float:
    scores = {
        "neutral": 20.0,
        "happy": 25.0,
        "surprise": 45.0,
        "sad": 55.0,
        "fear": 75.0,
        "angry": 90.0,
        "disgust": 70.0,
    }
    return scores.get(str(emotion).lower(), 40.0)


def stress_level(score: float) -> str:
    score_val = clamp(score)
    if score_val < 30.0:
        return "Low"
    elif score_val < 60.0:
        return "Moderate"
    elif score_val < 80.0:
        return "High"
    return "Extreme"