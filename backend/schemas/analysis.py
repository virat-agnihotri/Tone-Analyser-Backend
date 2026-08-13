from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class AnalysisRequest(BaseModel):
    session_id: int


class AnalysisResponse(BaseModel):
    session_id: int
    transcript: str
    emotion: str
    emotion_confidence: float
    stress_score: float
    stress_level: str
    audio_features: Dict[str, Any]
    insights: str
    recommendations: List[str]