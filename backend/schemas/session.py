from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    driver_name: str
    track_name: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    driver_name: str
    track_name: Optional[str] = None
    audio_path: Optional[str] = None
    status: str

    class Config:
        from_attributes = True