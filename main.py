from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # Ensures all SQLAlchemy models are registered with Base metadata before create_all

from routers import audio, analysis, sessions, reports

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Silent Co-Driver API",
    description="AI-powered driver communication, emotion classification, and vocal stress telemetry.",
    version="1.0.0"
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/")
def root():
    return {
        "title": "Silent Co-Driver API",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}