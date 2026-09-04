from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base

class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(Integer, primary_key=True, index=True)
    canonical_term = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, default="entity")  # person, brand, technical, etc.
    context_hint = Column(Text, nullable=True)     # optional context words or description
    
    # Phonetic signatures
    soundex = Column(String, index=True)
    metaphone = Column(String, index=True)
    nysiis = Column(String, index=True)
    
    # Memory mechanics
    frequency = Column(Integer, default=1)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)