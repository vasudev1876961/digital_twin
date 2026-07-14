# Digital Human Twin: AI-Powered Personalized Conversational Replica

This project is an AI-powered conversational replica of **Vasu**. It integrates speech processing, Large Language Models (Gemini API), Retrieval-Augmented Generation (RAG), long-term SQLite database memory, response validation, explainability traces, and cloned voice synthesis.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ and a virtual environment set up.

### 2. Configure Environment Variables
Create a `.env` file in the root directory (a template is provided in `.env`):
```ini
GEMINI_API_KEY=your_gemini_api_key_here
WHISPER_MODEL_NAME=base
XTTS_SPEAKER_REF=voice_samples/reference/vasu_ref.wav
SQLITE_DB_PATH=database/sqlite/digital_twin.db
CHROMA_DB_PATH=database/chroma
PERSONA_PROFILE=vasu
```

### 3. Place Voice Reference Sample
For **XTTS-v2 Voice Cloning** to clone your voice, place a clean 5-10 second WAV file of you speaking at:
`voice_samples/reference/vasu_ref.wav`

*Note: If no reference WAV is present, the twin will automatically fallback to standard Google Text-to-Speech (gTTS).*

### 4. Running the System
You can start both the FastAPI backend and Streamlit frontend concurrently using:
```bash
python run.py
```

Or run them individually:
* **API Backend Only**: `python run.py --api`
* **Streamlit Frontend Only**: `python run.py --frontend`

---

## 📂 Project Architecture

```
├── app/                  # FastAPI Backend routes, dependencies, configs
├── frontend/             # Streamlit application dashboards
├── models/               # Whisper STT, Gemini LLM, XTTS-v2 TTS, Embeddings
├── personality/          # Vasu's traits, speaking styles, prompt builder
├── memory/               # Short-term (RAM) and Long-term (SQLite) memories
├── rag/                  # Document parsing, chunking, retrieval
├── explainability/       # Attribution score and reasoning trace calculations
├── validators/           # Persona compliance & Hallucination checkers
├── database/             # SQLite and ChromaDB files
└── documents/            # Ingestion folders (resume, projects, certificates, notes)
```
