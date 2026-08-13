from pydantic import BaseModel
from typing import Optional


class LapDataCreate(BaseModel):
    lap_number: int
    lap_time: Optional[float] = None
    sector_time: Optional[float] = None
    max_speed: Optional[float] = None
    avg_speed: Optional[float] = None
    braking_events: Optional[int] = None
    throttle: Optional[float] = None


class LapDataResponse(LapDataCreate):
    id: int
    session_id: int

    class Config:
        from_attributes = True