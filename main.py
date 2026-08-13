from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from routers import audio, analysis, sessions, reports


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Silent Co-Driver API",
    description="AI-powered driver communication, emotion classification, and vocal stress telemetry.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",

        # ACTUAL VERCEL FRONTEND
        "https://tone-analyser-frontenddd.vercel.app",
    ],

    allow_origin_regex=r"https://tone-analyser-frontenddd.*\.vercel\.app",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    sessions.router,
    prefix="/api/sessions",
    tags=["Sessions"]
)

app.include_router(
    audio.router,
    prefix="/api/audio",
    tags=["Audio"]
)

app.include_router(
    analysis.router,
    prefix="/api/analysis",
    tags=["Analysis"]
)

app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Reports"]
)


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