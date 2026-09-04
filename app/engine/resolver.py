import re
from sqlalchemy.orm import Session
from app.engine.memory import MemoryStore

class TranscriptResolver:
    def __init__(self, db: Session):
        self.memory = MemoryStore(db)

    def resolve(self, asr_text: str, formatted_text: str) -> dict:
        tokens = re.findall(r"\b[\w'-]+\b", formatted_text)
        substitutions = []
        logs = []
        resolved_text = formatted_text

        for token in tokens:
            if len(token) <= 2:
                continue

            candidates = self.memory.find_candidates(token)
            if not candidates:
                logs.append({
                    "token": token,
                    "action": "no_action",
                    "reason": "No matching phonetic memory in store"
                })
                continue

            best = candidates[0]

            # Rule 1: Deliberate Inaction if token already matches canonical form
            if token == best["canonical_term"]:
                logs.append({
                    "token": token,
                    "action": "no_action",
                    "reason": "Token already matches canonical spelling"
                })
                continue

            # Rule 2: Deliberate Inaction for plain lower-case common words (e.g., fruit 'kiwi')
            # If the user's formatted transcript left it lower-case, and canonical is Proper Case,
            # preserve original intention unless strong context matches.
            if token.islower() and best["canonical_term"][0].isupper():
                logs.append({
                    "token": token,
                    "action": "no_action",
                    "reason": "Preserved lowercase common noun; avoided false-positive entity substitution"
                })
                continue

            # Perform boundary replacement
            pattern = re.compile(rf"\b{re.escape(token)}\b")
            resolved_text, count = pattern.subn(best["canonical_term"], resolved_text)

            if count > 0:
                action_info = {
                    "token": token,
                    "replaced_with": best["canonical_term"],
                    "action": "intervened",
                    "method": best["method"],
                    "score": round(best["score"], 3),
                    "confidence": best["confidence"],
                    "reason": f"Matched memory term '{best['canonical_term']}' via {best['method']}"
                }
                substitutions.append(action_info)
                logs.append(action_info)

        return {
            "asr_text": asr_text,
            "formatted_text": formatted_text,
            "memory_aware_text": resolved_text,
            "interventions_count": len(substitutions),
            "substitutions": substitutions,
            "logs": logs
        }