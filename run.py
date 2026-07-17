import sys
import argparse
import subprocess
import threading
import os
from pathlib import Path
from app.config import Config

# Auto-relaunch script using virtual environment python if not already running in it
BASE_DIR = Path(__file__).resolve().parent
venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
if venv_python.exists() and sys.executable != str(venv_python):
    print(f"Detecting global Python. Relaunching in virtual environment: {venv_python}")
    res = subprocess.run([str(venv_python)] + sys.argv)
    sys.exit(res.returncode)


def run_api():
    print(f"Starting API server on {Config.HOST}:{Config.PORT}...")
    import uvicorn
    # Disable reload=True to avoid threading signal exceptions on Windows
    uvicorn.run("app.main:app", host=Config.HOST, port=Config.PORT, reload=False)

def run_frontend():
    print("Starting Streamlit Frontend...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"
    ])

def main():
    parser = argparse.ArgumentParser(description="Digital Human Twin runner script")
    parser.add_argument("--api", action="store_true", help="Run FastAPI API server")
    parser.add_argument("--frontend", action="store_true", help="Run Streamlit frontend")
    parser.add_argument("--all", action="store_true", help="Run both API server and frontend")

    args = parser.parse_args()

    # If no flags are passed, default to --all
    if not (args.api or args.frontend or args.all):
        args.all = True

    threads = []

    if args.all or args.api:
        api_thread = threading.Thread(target=run_api, daemon=True)
        threads.append(api_thread)
        api_thread.start()

    if args.all or args.frontend:
        # Frontend is blocking when in main thread, but run in thread if running --all
        if args.all:
            frontend_thread = threading.Thread(target=run_frontend, daemon=True)
            threads.append(frontend_thread)
            frontend_thread.start()
        else:
            run_frontend()

    # Keep main thread alive if threads are running in background
    if args.all or args.api:
        for t in threads:
            try:
                t.join()
            except KeyboardInterrupt:
                print("Stopping services...")
                break

if __name__ == "__main__":
    main()
