import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent

VISUAL_GRAPH_DIR = BASE_DIR / "app" / "visual_graph"
VISUAL_GRAPH_DIR.mkdir(exist_ok=True)


# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# DATABASE_URL
DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")


ERP_LOGIN_URL = os.getenv("ERP_LOGIN_URL")
ERP_PASSWORD = os.getenv("ERP_PASSWORD")


