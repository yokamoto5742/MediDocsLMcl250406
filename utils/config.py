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


def parse_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        return {
            "host": parsed.hostname,
            "port": parsed.port,
            "user": parsed.username,
            "password": parsed.password,
            "database": parsed.path[1:]
        }
    return None

db_config = parse_database_url()

if db_config:
    POSTGRES_HOST = db_config["host"]
    POSTGRES_PORT = db_config["port"]
    POSTGRES_USER = db_config["user"]
    POSTGRES_PASSWORD = db_config["password"]
    POSTGRES_DB = db_config["database"]
    POSTGRES_SSL = "require"
else:
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "discharge_summary_app")
    POSTGRES_SSL = os.environ.get("POSTGRES_SSL", None)

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
MAX_TOKEN_THRESHOLD = int(os.environ.get("MAX_TOKEN_THRESHOLD", "40000"))

APP_TYPE = os.environ.get("APP_TYPE", "default")
