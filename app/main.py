from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.engine.memory import MemoryStore
from app.engine.resolver import TranscriptResolver

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kivi Phonetic Memory Engine")

# Serve static files for UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class LearnRequest(BaseModel):
    canonical_term: str
    category: str = "entity"
    context_hint: str | None = None

class ResolveRequest(BaseModel):
    asr_text: str
    formatted_text: str

@app.get("/")
def serve_home():
    return FileResponse("app/static/index.html")

@app.post("/api/learn")
def learn_term(payload: LearnRequest, db: Session = Depends(get_db)):
    store = MemoryStore(db)
    entry = store.learn_term(
        canonical_term=payload.canonical_term,
        category=payload.category,
        context_hint=payload.context_hint
    )
    return {
        "status": "success",
        "entry": {
            "id": entry.id,
            "canonical_term": entry.canonical_term,
            "category": entry.category,
            "frequency": entry.frequency,
            "confidence": entry.confidence,
            "metaphone": entry.metaphone
        }
    }

@app.get("/api/memory")
def get_memory(db: Session = Depends(get_db)):
    store = MemoryStore(db)
    entries = store.get_all_entries()
    return [
        {
            "id": e.id,
            "canonical_term": e.canonical_term,
            "category": e.category,
            "frequency": e.frequency,
            "confidence": e.confidence,
            "soundex": e.soundex,
            "metaphone": e.metaphone,
            "nysiis": e.nysiis,
            "last_updated": e.last_updated.isoformat() if e.last_updated else None
        }
        for e in entries
    ]

@app.post("/api/resolve")
def resolve_transcript(payload: ResolveRequest, db: Session = Depends(get_db)):
    resolver = TranscriptResolver(db)
    return resolver.resolve(payload.asr_text, payload.formatted_text)

@app.post("/api/reset")
def reset_memory(db: Session = Depends(get_db)):
    store = MemoryStore(db)
    store.reset_all()
    return {"status": "success", "message": "Memory store wiped clean."}