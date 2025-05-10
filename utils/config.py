import configparser
import os
from pathlib import Path

from dotenv import load_dotenv


def get_config():
    config = configparser.ConfigParser()
    base_dir = Path(__file__).parent.parent
    config_path = os.path.join(base_dir, 'config.ini')

    config.read(config_path, encoding='utf-8')

    return config

load_dotenv()

# PostgreSQL設定
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "discharge_summary_app")

# API設定
GEMINI_CREDENTIALS = os.environ.get("GEMINI_CREDENTIALS")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
GEMINI_FLASH_MODEL = os.environ.get("GEMINI_FLASH_MODEL")
GEMINI_THINKING_BUDGET = int(os.environ.get("GEMINI_THINKING_BUDGET", "0")) if os.environ.get("GEMINI_THINKING_BUDGET") else None

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

SELECTED_AI_MODEL = os.environ.get("SELECTED_AI_MODEL", "gemini")

MAX_INPUT_TOKENS = int(os.environ.get("MAX_INPUT_TOKENS", "200000"))
MIN_INPUT_TOKENS = int(os.environ.get("MIN_INPUT_TOKENS", "100"))