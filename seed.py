from app.database import engine, Base, SessionLocal
from app.engine.memory import MemoryStore

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    store = MemoryStore(db)
    
    initial_terms = [
        ("Aaditya", "person", "coworker / engineer"),
        ("Kivi", "brand", "Sarvam speech app"),
        ("Sarvam", "brand", "parent AI lab"),
        ("Karthick", "person", "team lead")
    ]
    
    for term, category, hint in initial_terms:
        store.learn_term(term, category, hint)
        
    db.close()
    print("Database successfully seeded with standard phonetic memories.")

if __name__ == "__main__":
    seed_database()