from sqlalchemy import create_engine, text
import time
from utils.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, 
    POSTGRES_PASSWORD, POSTGRES_DB
)
from utils.exceptions import DatabaseError
from database.db import DatabaseManager


def create_tables():
    db_manager = DatabaseManager.get_instance()
    engine = db_manager.get_engine()

    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password BYTEA NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    departments_table = """
    CREATE TABLE IF NOT EXISTS departments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        order_index INTEGER NOT NULL,
        default_model VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    prompts_table = """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        department VARCHAR(100) NOT NULL,
        name VARCHAR(100) NOT NULL,
        content TEXT NOT NULL,
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_department_prompt UNIQUE (department, name)
    );
    """

    summary_usage_table = """
    CREATE TABLE IF NOT EXISTS summary_usage (
        id SERIAL PRIMARY KEY,
        date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        app_type VARCHAR(50),
        document_name VARCHAR(100),
        model_detail VARCHAR(100),
        department VARCHAR(100),
        input_tokens INTEGER,
        output_tokens INTEGER,
        total_tokens INTEGER,
        processing_time INTEGER
    );
    """

    app_settings_table = """
    CREATE TABLE IF NOT EXISTS app_settings (
        id SERIAL PRIMARY KEY,
        setting_id VARCHAR(100) UNIQUE NOT NULL,
        selected_department VARCHAR(100),
        selected_model VARCHAR(50),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    document_types_table = """
                           CREATE TABLE IF NOT EXISTS document_types \
                           ( \
                               id \
                               SERIAL \
                               PRIMARY \
                               KEY, \
                               name \
                               VARCHAR \
                           ( \
                               100 \
                           ) UNIQUE NOT NULL,
                               order_index INTEGER NOT NULL,
                               created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                        ); \
                           """

    try:
        with engine.begin() as conn:
            conn.execute(text(users_table))
            conn.execute(text(departments_table))
            conn.execute(text(prompts_table))
            conn.execute(text(summary_usage_table))
            conn.execute(text(app_settings_table))
            conn.execute(text(document_types_table))
        return True
    except Exception as e:
        raise DatabaseError(f"テーブル作成中にエラーが発生しました: {str(e)}")


def initialize_database():
    max_retries = 5
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            create_tables()
            return True
        except Exception as e:
            last_error = e
            retry_count += 1
            wait_time = 2 ** retry_count  # 指数バックオフ
            print(f"データベース初期化に失敗しました（試行 {retry_count}/{max_retries}）: {str(e)}")
            print(f"{wait_time}秒後に再試行します...")
            time.sleep(wait_time)
    
    # 全リトライが失敗した場合
    raise DatabaseError(f"データベースの初期化に失敗しました: {str(last_error)}")
