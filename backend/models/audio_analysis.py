from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from database import Base


class AudioAnalysis(Base):
    __tablename__ = "audio_analysis"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(Float, nullable=True, default=0.0)
    transcript = Column(Text, nullable=True)
    emotion = Column(String, nullable=True)
    emotion_confidence = Column(Float, nullable=True)
    stress_score = Column(Float, nullable=True)
    pitch_mean = Column(Float, nullable=True)
    energy_mean = Column(Float, nullable=True)
    speaking_rate = Column(Float, nullable=True)