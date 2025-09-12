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

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL")

CLAUDE_API_KEY = True if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, ANTHROPIC_MODEL]) else None
CLAUDE_MODEL = ANTHROPIC_MODEL  # モデル名も互換性のため維持

SELECTED_AI_MODEL = os.environ.get("SELECTED_AI_MODEL", "claude")

MAX_INPUT_TOKENS = int(os.environ.get("MAX_INPUT_TOKENS", "300000"))
MIN_INPUT_TOKENS = int(os.environ.get("MIN_INPUT_TOKENS", "100"))
MAX_TOKEN_THRESHOLD = int(os.environ.get("MAX_TOKEN_THRESHOLD", "100000"))
PROMPT_MANAGEMENT = os.environ.get("PROMPT_MANAGEMENT", "False").lower() == "true"

APP_TYPE = os.environ.get("APP_TYPE", "default")
