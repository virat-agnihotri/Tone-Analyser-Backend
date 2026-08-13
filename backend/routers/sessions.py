from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List

from database import get_db
from models.session import Session as SessionModel
from models.lap_data import LapData
from schemas.session import SessionCreate, SessionResponse
from schemas.lap import LapDataCreate, LapDataResponse

router = APIRouter()


@router.post("/", response_model=SessionResponse)
def create_session(data: SessionCreate, db: DBSession = Depends(get_db)):
    session = SessionModel(
        driver_name=data.driver_name,
        track_name=data.track_name,
        status="created"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=List[SessionResponse])
def get_sessions(db: DBSession = Depends(get_db)):
    return db.query(SessionModel).order_by(SessionModel.created_at.desc()).all()


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")
    return session


@router.post("/{session_id}/laps", response_model=LapDataResponse)
def add_lap_telemetry(session_id: int, data: LapDataCreate, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    lap_record = LapData(
        session_id=session_id,
        lap_number=data.lap_number,
        lap_time=data.lap_time,
        sector_time=data.sector_time,
        max_speed=data.max_speed,
        avg_speed=data.avg_speed,
        braking_events=data.braking_events,
        throttle=data.throttle
    )

    db.add(lap_record)
    db.commit()
    db.refresh(lap_record)
    return lap_record


@router.get("/{session_id}/laps", response_model=List[LapDataResponse])
def get_session_laps(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    return db.query(LapData).filter(LapData.session_id == session_id).order_by(LapData.lap_number.asc()).all()