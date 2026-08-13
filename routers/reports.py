from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models.session import Session as SessionModel
from models.audio_analysis import AudioAnalysis
from models.lap_data import LapData

router = APIRouter()


@router.get("/{session_id}")
def get_report(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    analysis_records = (
        db.query(AudioAnalysis)
        .filter(AudioAnalysis.session_id == session_id)
        .order_by(AudioAnalysis.timestamp.asc(), AudioAnalysis.id.asc())
        .all()
    )

    # Find primary analysis record (has non-empty transcript or overall summary)
    primary_analysis = next(
        (r for r in analysis_records if r.transcript and r.transcript.strip()),
        analysis_records[0] if analysis_records else None
    )

    laps = (
        db.query(LapData)
        .filter(LapData.session_id == session_id)
        .order_by(LapData.lap_number.asc())
        .all()
    )

    return {
        "session": session,
        "latest_analysis": primary_analysis,
        "all_analysis_records": analysis_records,
        "lap_data": laps
    }