from datetime import datetime
from sqlalchemy.orm import Session
from app.models import MemoryEntry
from app.engine.phonetics import compute_phonetic_signatures, match_score

class MemoryStore:
    def __init__(self, db: Session):
        self.db = db

    def learn_term(self, canonical_term: str, category: str = "entity", context_hint: str = None) -> MemoryEntry:
        term = canonical_term.strip()
        entry = self.db.query(MemoryEntry).filter(MemoryEntry.canonical_term.ilike(term)).first()

        if entry:
            entry.frequency += 1
            entry.confidence = min(1.0, entry.confidence + 0.05)
            entry.last_updated = datetime.utcnow()
            if context_hint:
                entry.context_hint = context_hint
        else:
            sigs = compute_phonetic_signatures(term)
            entry = MemoryEntry(
                canonical_term=term,
                category=category,
                context_hint=context_hint,
                soundex=sigs["soundex"],
                metaphone=sigs["metaphone"],
                nysiis=sigs["nysiis"],
                frequency=1,
                confidence=1.0
            )
            self.db.add(entry)

        self.db.commit()
        self.db.refresh(entry)
        return entry

    def find_candidates(self, token: str, threshold: float = 0.82) -> list[dict]:
        entries = self.db.query(MemoryEntry).all()
        matches = []
        for e in entries:
            is_match, score, method = match_score(token, e.canonical_term)
            if is_match and score >= threshold:
                matches.append({
                    "id": e.id,
                    "canonical_term": e.canonical_term,
                    "category": e.category,
                    "context_hint": e.context_hint,
                    "score": score,
                    "method": method,
                    "confidence": e.confidence,
                    "frequency": e.frequency
                })
        # Sort by confidence and phonetic similarity
        matches.sort(key=lambda x: (x["score"], x["confidence"], x["frequency"]), reverse=True)
        return matches

    def get_all_entries(self) -> list[MemoryEntry]:
        return self.db.query(MemoryEntry).order_by(MemoryEntry.frequency.desc()).all()

    def reset_all(self):
        self.db.query(MemoryEntry).delete()
        self.db.commit()