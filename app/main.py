try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import chat, audio, documents, health, memory, persona
from utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="Digital Human Twin API",
    description="Backend services for Vasu's Digital Human Twin conversational replica.",
    version="1.0.0",
    debug=Config.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(audio.router)
app.include_router(documents.router)
app.include_router(memory.router)
app.include_router(persona.router)

@app.on_event("startup")
def startup_event():
    logger.info("Starting up Digital Human Twin API...")
    Config.ensure_directories()
    # Lazy dependency check on startup
    try:
        from app.dependencies import get_db
        next(get_db())
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Digital Human Twin API...")
