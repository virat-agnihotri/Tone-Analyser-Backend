from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models.session import Session as SessionModel
from utils.audio_utils import save_audio, convert_to_wav

router = APIRouter()

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg"}


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    filename = file.filename or "audio.wav"
    extension = f".{filename.lower().split('.')[-1]}" if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format. Allowed: {ALLOWED_EXTENSIONS}")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    try:
        raw_path = save_audio(data, filename)
        wav_path = convert_to_wav(raw_path)
        return {
            "message": "Audio uploaded and processed successfully",
            "audio_path": wav_path
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Audio processing error: {str(error)}")


@router.post("/upload/{session_id}")
async def upload_audio_for_session(
    session_id: int,
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found")

    filename = file.filename or "audio.wav"
    extension = f".{filename.lower().split('.')[-1]}" if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format. Allowed: {ALLOWED_EXTENSIONS}")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    try:
        raw_path = save_audio(data, filename)
        wav_path = convert_to_wav(raw_path)

        session.audio_path = wav_path
        session.status = "uploaded"
        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "audio_path": wav_path,
            "status": "uploaded"
        }
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(error)}")