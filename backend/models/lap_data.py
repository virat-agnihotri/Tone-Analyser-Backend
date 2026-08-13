from sqlalchemy import Column, Integer, Float, ForeignKey
from database import Base


class LapData(Base):
    __tablename__ = "lap_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    lap_number = Column(Integer, nullable=False)
    lap_time = Column(Float, nullable=True)
    sector_time = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)
    avg_speed = Column(Float, nullable=True)
    braking_events = Column(Integer, nullable=True)
    throttle = Column(Float, nullable=True)