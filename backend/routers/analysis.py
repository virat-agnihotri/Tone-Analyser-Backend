import librosa
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models.session import Session as SessionModel
from models.audio_analysis import AudioAnalysis
from models.lap_data import LapData

from services.audio_features import extract_audio_features, extract_audio_features_from_samples
from services.transcription import transcribe_audio
from services.emotion import analyze_emotion, analyze_emotion_from_samples
from services.stress_engine import calculate_stress
from services.lap_analysis import analyze_lap_data
from services.rag import retrieve_context
from services.llm import generate_insights, generate_recommendations

router = APIRouter()


@router.post("/{session_id}")
def analyze_session(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found.")

    if not session.audio_path or not Path(session.audio_path).exists():
        raise HTTPException(status_code=400, detail="No valid audio file attached to session.")

    session.status = "processing"
    db.commit()

    try:
        # Load audio into memory once for all pipeline steps
        y, sr = librosa.load(session.audio_path, sr=16000, mono=True)
        if len(y) == 0:
            raise ValueError("Audio file is empty.")

        # Clean previous analysis records for clean re-analysis
        db.query(AudioAnalysis).filter(AudioAnalysis.session_id == session_id).delete()
        db.commit()

        # 1. Overall Acoustic Features
        audio_features = extract_audio_features_from_samples(y, sr)

        # 2. Speech-to-Text Transcription
        transcription = transcribe_audio(session.audio_path)
        transcript_text = transcription.get("text", "")

        # 3. Overall Emotion Detection
        emotion = analyze_emotion_from_samples(y, sr)

        # 4. Overall Stress Estimation
        stress = calculate_stress(audio_features, emotion)

        # 5. Lap & Telemetry Analysis
        laps_db = db.query(LapData).filter(LapData.session_id == session_id).all()
        lap_dicts = [
            {
                "lap_number": l.lap_number,
                "lap_time": l.lap_time,
                "sector_time": l.sector_time,
                "max_speed": l.max_speed,
                "avg_speed": l.avg_speed,
                "braking_events": l.braking_events,
                "throttle": l.throttle,
            }
            for l in laps_db
        ]
        lap_analysis = analyze_lap_data(lap_dicts, stress["score"])

        # 6. RAG Knowledge Retrieval
        context = retrieve_context(transcript_text, top_k=3)

        # 7. LLM Insights & Recommendations
        insights = generate_insights(
            transcript=transcript_text,
            stress=stress,
            emotion=emotion,
            lap_data=lap_analysis,
            context=context
        )
        recommendations = generate_recommendations(insights)

        # 8. Save Overall Analysis Record (timestamp 0.0)
        overall_record = AudioAnalysis(
            session_id=session_id,
            timestamp=0.0,
            transcript=transcript_text,
            emotion=emotion.get("emotion"),
            emotion_confidence=emotion.get("confidence"),
            stress_score=stress.get("score"),
            pitch_mean=audio_features.get("pitch_mean"),
            energy_mean=audio_features.get("energy_mean"),
            speaking_rate=audio_features.get("speaking_ratio")
        )
        db.add(overall_record)

        # 9. Adaptive Segment-Level Analysis
        total_duration = len(y) / sr

        if total_duration >= 6.0:
            segment_duration = 3.0
        elif total_duration >= 2.0:
            segment_duration = 1.0
        else:
            segment_duration = total_duration

        if total_duration >= 1.5:
            current_start = 0.0
            while current_start < total_duration:
                current_end = min(current_start + segment_duration, total_duration)
                seg_y = y[int(current_start * sr) : int(current_end * sr)]

                # Process segment if it has at least 0.3s of audio
                if len(seg_y) >= int(sr * 0.3):
                    seg_features = extract_audio_features_from_samples(seg_y, sr)
                    seg_emotion = analyze_emotion_from_samples(seg_y, sr)
                    seg_stress = calculate_stress(seg_features, seg_emotion)

                    seg_record = AudioAnalysis(
                        session_id=session_id,
                        timestamp=round(current_start, 2),
                        transcript="",
                        emotion=seg_emotion.get("emotion"),
                        emotion_confidence=seg_emotion.get("confidence"),
                        stress_score=seg_stress.get("score"),
                        pitch_mean=seg_features.get("pitch_mean"),
                        energy_mean=seg_features.get("energy_mean"),
                        speaking_rate=seg_features.get("speaking_ratio")
                    )
                    db.add(seg_record)

                current_start += segment_duration


        session.status = "completed"
        db.commit()

        # Fetch all saved analysis records in timestamp order
        all_analysis_records = (
            db.query(AudioAnalysis)
            .filter(AudioAnalysis.session_id == session_id)
            .order_by(AudioAnalysis.timestamp.asc(), AudioAnalysis.id.asc())
            .all()
        )

        return {
            "session_id": session_id,
            "transcript": transcription,
            "emotion": emotion,
            "stress": stress,
            "audio_features": audio_features,
            "lap_analysis": lap_analysis,
            "rag_context": context,
            "insights": insights,
            "recommendations": recommendations,
            "all_analysis_records": all_analysis_records,
        }

    except Exception as error:
        session.status = "failed"
        db.commit()
        print(f"Error during session #{session_id} analysis: {error}")
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(error)}")