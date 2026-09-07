# Kivi Phonetic Memory System

An adaptive word-level phonetic memory engine designed for Kivi by Sarvam AI. It personalizes speech-to-text transcripts by mapping phonetic variations to user-specific canonical spellings.

## Architectural Overview
- **Storage Layer**: SQLite backed by SQLAlchemy, tracking canonical terms, phonetic signatures, usage frequency, and confidence scores.
- **Phonetic Matching Engine**: Multi-stage phonetic normalizer utilizing Metaphone, NYSIIS, and phonetic interchangeability rules (such as $V \leftrightarrow W$ mappings and double-vowel reduction common in regional speech).
- **Resolver**: Tokenizes incoming transcripts, scores candidates against stored memory signatures, and logs decision provenance.
- **Deliberate Inaction**: Guardrails preserve lowercase common nouns to prevent false-positive entity substitutions (e.g., preserving fruit 'kiwi' while correcting brand 'Kivi').

## Project Structure
- `app/engine/phonetics.py`: Phonetic encoders and similarity scoring algorithms.
- `app/engine/memory.py`: CRUD, confidence updating, and candidate retrieval.
- `app/engine/resolver.py`: Transcript transformation and transparency logging.
- `app/static/index.html`: Interactive inspection and test interface.
- `evaluation/`: Benchmark dataset, test harness, and evaluation logs.

For execution instructions, refer to `RUN.md`.
