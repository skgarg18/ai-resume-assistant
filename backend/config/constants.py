# Directory to storage file of log

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # Resume AI filter
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Frontend  URL

FRONTEND_URL = "http://localhost:3000"


