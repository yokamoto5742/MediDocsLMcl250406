"""
MongoDBからPostgreSQLへのデータ移行スクリプト

このスクリプトは既存のMongoDBデータベースからPostgreSQL
データベースへデータを移行します。

使い方:
python migrate_mongodb_to_postgres.py
"""

import os
import datetime
import logging
import time

from pymongo import MongoClient
import psycopg2
from psycopg2.extras import Json, DictCursor
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migration")

# 環境変数の読み込み（エンコーディングを指定）
load_dotenv(encoding='utf-8')

# MongoDB設定
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB = os.environ.get("MONGODB_DB_NAME", "discharge_summary_app")

# PostgreSQL設定
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "discharge_summary_app")

# Windows環境での文字エンコーディング問題に対処
import sys

if sys.platform == 'win32':
    # コンソール出力のエンコーディング設定
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    # 環境変数のエンコーディング修正
    try:
        if POSTGRES_PASSWORD:
            POSTGRES_PASSWORD = POSTGRES_PASSWORD.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # エラーが発生した場合は、そのまま使用
        pass

def connect_mongodb():
    """MongoDBに接続する"""
    if not MONGODB_URI:
        raise ValueError("MongoDB接続URIが設定されていません")
    
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    logger.info(f"MongoDBデータベース {MONGODB_DB} に接続しました")
    return client, db


def connect_postgres():
    """PostgreSQLに接続する"""
    try:
        # 環境変数から読み込んだパスワードのエンコーディングを確認
        password = POSTGRES_PASSWORD
        if isinstance(password, bytes):
            password = password.decode('utf-8', errors='replace')

        # 接続文字列を作成（エンコーディングを明示的に指定）
        conn_string = f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={password} client_encoding=utf8"

        conn = psycopg2.connect(conn_string)
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor(cursor_factory=DictCursor)
        logger.info(f"PostgreSQLデータベース {POSTGRES_DB} に接続しました")
        return conn, cursor
    except Exception as e:
        logger.error(f"PostgreSQL接続エラー: {str(e)}")
        # デバッグ情報を追加
        logger.debug(
            f"接続情報 - Host: {POSTGRES_HOST}, Port: {POSTGRES_PORT}, DB: {POSTGRES_DB}, User: {POSTGRES_USER}")
        raise


def migrate_departments(mongo_db, pg_cursor):
    """診療科データを移行する"""
    departments = mongo_db.departments.find().sort("order", 1)
    count = 0
    
    for dept in departments:
        try:
            # MongoDBのデータをPostgreSQL形式に変換
            order_index = dept.get("order", 0)
            name = dept.get("name")
            default_model = dept.get("default_model")
            created_at = dept.get("created_at", datetime.datetime.now())
            updated_at = dept.get("updated_at", datetime.datetime.now())
            
            # PostgreSQLにデータを挿入
            insert_query = """
            INSERT INTO departments (name, order_index, default_model, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE 
            SET order_index = EXCLUDED.order_index,
                default_model = EXCLUDED.default_model,
                updated_at = EXCLUDED.updated_at
            """
            pg_cursor.execute(insert_query, (name, order_index, default_model, created_at, updated_at))
            count += 1
            
        except Exception as e:
            logger.error(f"診療科 '{dept.get('name', 'unknown')}' の移行中にエラー: {str(e)}")
    
    logger.info(f"{count}件の診療科データを移行しました")
    return count


def migrate_prompts(mongo_db, pg_cursor):
    """プロンプトデータを移行する"""
    prompts = mongo_db.prompts.find()
    count = 0
    
    for prompt in prompts:
        try:
            # MongoDBのデータをPostgreSQL形式に変換
            department = prompt.get("department", "default")
            name = prompt.get("name", "")
            content = prompt.get("content", "")
            is_default = prompt.get("is_default", False)
            created_at = prompt.get("created_at", datetime.datetime.now())
            updated_at = prompt.get("updated_at", datetime.datetime.now())
            
            # PostgreSQLにデータを挿入
            insert_query = """
            INSERT INTO prompts (department, name, content, is_default, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT unique_department_prompt DO UPDATE 
            SET content = EXCLUDED.content,
                is_default = EXCLUDED.is_default,
                updated_at = EXCLUDED.updated_at
            """
            pg_cursor.execute(insert_query, (department, name, content, is_default, created_at, updated_at))
            count += 1
            
        except Exception as e:
            logger.error(f"プロンプト '{prompt.get('name', 'unknown')}' の移行中にエラー: {str(e)}")
    
    logger.info(f"{count}件のプロンプトデータを移行しました")
    return count


def migrate_users(mongo_db, pg_cursor):
    """ユーザーデータを移行する"""
    users = mongo_db.users.find()
    count = 0
    
    for user in users:
        try:
            # MongoDBのデータをPostgreSQL形式に変換
            username = user.get("username")
            password = user.get("password")  # すでにbcryptでハッシュ化されたバイト列
            is_admin = user.get("is_admin", False)
            created_at = user.get("created_at", datetime.datetime.now())
            updated_at = user.get("updated_at", datetime.datetime.now())
            
            # PostgreSQLにデータを挿入
            insert_query = """
            INSERT INTO users (username, password, is_admin, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE 
            SET password = EXCLUDED.password,
                is_admin = EXCLUDED.is_admin,
                updated_at = EXCLUDED.updated_at
            """
            pg_cursor.execute(insert_query, (username, password, is_admin, created_at, updated_at))
            count += 1
            
        except Exception as e:
            logger.error(f"ユーザー '{user.get('username', 'unknown')}' の移行中にエラー: {str(e)}")
    
    logger.info(f"{count}件のユーザーデータを移行しました")
    return count


def migrate_usage_stats(mongo_db, pg_cursor):
    """使用統計データを移行する"""
    usage_stats = mongo_db.summary_usage.find()
    count = 0
    
    for stat in usage_stats:
        try:
            # MongoDBのデータをPostgreSQL形式に変換
            date = stat.get("date", datetime.datetime.now())
            app_type = stat.get("app_type")
            document_name = stat.get("document_name")
            model_detail = stat.get("model_detail")
            department = stat.get("department", "default")
            input_tokens = stat.get("input_tokens", 0)
            output_tokens = stat.get("output_tokens", 0)
            total_tokens = stat.get("total_tokens", input_tokens + output_tokens)
            processing_time = stat.get("processing_time", 0)
            
            # PostgreSQLにデータを挿入
            insert_query = """
            INSERT INTO summary_usage 
            (date, app_type, document_name, model_detail, department, 
             input_tokens, output_tokens, total_tokens, processing_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            pg_cursor.execute(insert_query, (
                date, app_type, document_name, model_detail, department,
                input_tokens, output_tokens, total_tokens, processing_time
            ))
            count += 1
            
            # 大量のデータを処理する場合、適宜コミットする
            if count % 1000 == 0:
                pg_cursor.connection.commit()
                logger.info(f"{count}件の使用統計を処理中...")
                
        except Exception as e:
            logger.error(f"使用統計ID '{stat.get('_id', 'unknown')}' の移行中にエラー: {str(e)}")
    
    logger.info(f"{count}件の使用統計データを移行しました")
    return count


def migrate_settings(mongo_db, pg_cursor):
    """アプリ設定データを移行する"""
    settings = mongo_db.app_settings.find()
    count = 0
    
    for setting in settings:
        try:
            # MongoDBのデータをPostgreSQL形式に変換
            setting_id = setting.get("setting_id")
            selected_department = setting.get("selected_department")
            selected_model = setting.get("selected_model")
            updated_at = setting.get("updated_at", datetime.datetime.now())
            
            # PostgreSQLにデータを挿入
            insert_query = """
            INSERT INTO app_settings (setting_id, selected_department, selected_model, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (setting_id) DO UPDATE 
            SET selected_department = EXCLUDED.selected_department,
                selected_model = EXCLUDED.selected_model,
                updated_at = EXCLUDED.updated_at
            """
            pg_cursor.execute(insert_query, (setting_id, selected_department, selected_model, updated_at))
            count += 1
            
        except Exception as e:
            logger.error(f"設定 '{setting.get('setting_id', 'unknown')}' の移行中にエラー: {str(e)}")
    
    logger.info(f"{count}件の設定データを移行しました")
    return count


def main():
    """メイン処理"""
    start_time = time.time()
    logger.info("MongoDBからPostgreSQLへのデータ移行を開始します")
    
    try:
        # MongoDB接続
        mongo_client, mongo_db = connect_mongodb()
        
        # PostgreSQL接続
        pg_conn, pg_cursor = connect_postgres()
        
        try:
            # 移行処理を実行
            dept_count = migrate_departments(mongo_db, pg_cursor)
            prompt_count = migrate_prompts(mongo_db, pg_cursor)
            user_count = migrate_users(mongo_db, pg_cursor)
            stats_count = migrate_usage_stats(mongo_db, pg_cursor)
            settings_count = migrate_settings(mongo_db, pg_cursor)
            
            # 変更をコミット
            pg_conn.commit()
            
            # 移行結果の表示
            logger.info("-" * 50)
            logger.info("データ移行が完了しました")
            logger.info(f"診療科データ: {dept_count}件")
            logger.info(f"プロンプトデータ: {prompt_count}件")
            logger.info(f"ユーザーデータ: {user_count}件")
            logger.info(f"使用統計データ: {stats_count}件")
            logger.info(f"設定データ: {settings_count}件")
            logger.info(f"処理時間: {time.time() - start_time:.2f}秒")
            logger.info("-" * 50)
            
        except Exception as e:
            pg_conn.rollback()
            logger.error(f"移行処理中にエラーが発生しました: {str(e)}")
            raise
        finally:
            pg_cursor.close()
            pg_conn.close()
            mongo_client.close()
            
    except Exception as e:
        logger.error(f"移行処理に失敗しました: {str(e)}")
        logger.error("データ移行は中断されました")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
