import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.engine.memory import MemoryStore
from app.engine.resolver import TranscriptResolver

TEST_DB_URL = "sqlite:///./eval_test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_evaluation():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionTest()

    with open("evaluation/dataset.json", "r") as f:
        cases = json.load(f)

    results = []
    total_cases = len(cases)
    passed_cases = 0
    total_latency = 0.0

    print(f"\n--- Running Kivi Evaluation Suite ({total_cases} cases) ---")

    for case in cases:
        store = MemoryStore(db)
        store.reset_all()

        for st in case["seed_terms"]:
            store.learn_term(st["term"], st.get("category", "entity"))

        resolver = TranscriptResolver(db)
        
        t0 = time.perf_counter()
        resolution = resolver.resolve(case["asr_input"], case["formatted_input"])
        latency_ms = (time.perf_counter() - t0) * 1000.0
        total_latency += latency_ms

        actual_output = resolution["memory_aware_text"]
        intervened = resolution["interventions_count"] > 0
        expected_output = case["expected_output"]

        passed = (actual_output.strip() == expected_output.strip())
        if passed:
            passed_cases += 1

        db_size_bytes = os.path.getsize("eval_test.db") if os.path.exists("eval_test.db") else 0

        case_record = {
            "case_id": case["id"],
            "description": case["description"],
            "inputs": {
                "asr": case["asr_input"],
                "formatted": case["formatted_input"]
            },
            "expected_output": expected_output,
            "actual_output": actual_output,
            "passed": passed,
            "latency_ms": round(latency_ms, 3),
            "intervened": intervened,
            "expected_intervention": case["should_intervene"],
            "db_size_bytes": db_size_bytes,
            "logs": resolution["logs"]
        }
        results.append(case_record)
        status_label = "PASS" if passed else "FAIL"
        print(f"[{status_label}] {case['id']} - {round(latency_ms, 2)}ms")

    # Release DB connections for Windows file handle cleanup
    db.close()
    engine.dispose()

    if os.path.exists("eval_test.db"):
        try:
            os.remove("eval_test.db")
        except PermissionError:
            pass

    summary = {
        "total_cases": total_cases,
        "passed": passed_cases,
        "accuracy_pct": round((passed_cases / total_cases) * 100, 2),
        "avg_latency_ms": round(total_latency / total_cases, 3),
        "cases": results
    }

    with open("evaluation/results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nEvaluation Complete: {passed_cases}/{total_cases} passed. Results saved to evaluation/results.json\n")

if __name__ == "__main__":
    run_evaluation()