from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    driver_name = Column(String, nullable=False)
    track_name = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    status = Column(String, default="created")
    created_at = Column(DateTime, server_default=func.now())