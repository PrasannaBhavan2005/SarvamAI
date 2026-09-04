# Review Guide: Kivi Phonetic Memory Engine

## Primary Review Method
Completely local application running on FastAPI with an embedded SQLite database.

## 1. Runtimes and Versions
- Python 3.10+ (tested on Python 3.12)
- Git

## 2. Environment Variables
No external API keys or environment variables required. The matching and resolution pipeline runs entirely locally.

## 3. Dependency Installation
```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

pip install -r requirements.txt