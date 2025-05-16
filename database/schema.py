from sqlalchemy import create_engine, text
import time
import os
import importlib
from subprocess import run, PIPE
from utils.exceptions import DatabaseError
from database.db import DatabaseManager


def run_alembic_migrations():
    """Alembicマイグレーションを実行する関数"""
    try:
        # alembicがインストールされているか確認
        if importlib.util.find_spec("alembic") is None:
            print("警告: alembicがインストールされていません。マイグレーションはスキップされます。")
            return False

        # アプリケーションのルートディレクトリを取得
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # alembicコマンドを実行
        result = run(
            ["alembic", "upgrade", "head"],
            cwd=root_dir,
            stdout=PIPE,
            stderr=PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"警告: マイグレーション実行中にエラーが発生しました: {result.stderr}")
            return False

        print("データベースマイグレーションが正常に完了しました。")
        return True
    except Exception as e:
        print(f"マイグレーション実行中にエラーが発生しました: {str(e)}")
        return False


def create_tables():
    """
    従来のテーブル作成処理。
    Alembicマイグレーションが失敗した場合のフォールバックとして使用。
    """
    db_manager = DatabaseManager.get_instance()
    engine = db_manager.get_engine()

    users_table = """
                  CREATE TABLE IF NOT EXISTS users \
                  ( \
                      id \
                      SERIAL \
                      PRIMARY \
                      KEY, \
                      username \
                      VARCHAR \
                  ( \
                      100 \
                  ) UNIQUE NOT NULL,
                      password BYTEA NOT NULL,
                      is_admin BOOLEAN DEFAULT FALSE,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                               ); \
                  """

    departments_table = """
                        CREATE TABLE IF NOT EXISTS departments \
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
                            default_model VARCHAR \
                        ( \
                            50 \
                        ),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                     ); \
                        """

    prompts_table = """
                    CREATE TABLE IF NOT EXISTS prompts \
                    ( \
                        id \
                        SERIAL \
                        PRIMARY \
                        KEY, \
                        department \
                        VARCHAR \
                    ( \
                        100 \
                    ) NOT NULL,
                        document_type VARCHAR \
                    ( \
                        100 \
                    ) NOT NULL,
                        doctor VARCHAR \
                    ( \
                        100 \
                    ) NOT NULL,
                        name VARCHAR \
                    ( \
                        100 \
                    ) NOT NULL,
                        content TEXT NOT NULL,
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                                                 CONSTRAINT unique_prompt UNIQUE (department, document_type, doctor, name)
                        ); \
                    """

    summary_usage_table = """
                          CREATE TABLE IF NOT EXISTS summary_usage \
                          ( \
                              id \
                              SERIAL \
                              PRIMARY \
                              KEY, \
                              date \
                              TIMESTAMP \
                              WITH \
                              TIME \
                              ZONE \
                              DEFAULT \
                              CURRENT_TIMESTAMP, \
                              app_type \
                              VARCHAR \
                          ( \
                              50 \
                          ),
                              document_name VARCHAR \
                          ( \
                              100 \
                          ),
                              model_detail VARCHAR \
                          ( \
                              100 \
                          ),
                              department VARCHAR \
                          ( \
                              100 \
                          ),
                              input_tokens INTEGER,
                              output_tokens INTEGER,
                              total_tokens INTEGER,
                              processing_time INTEGER
                              ); \
                          """

    app_settings_table = """
                         CREATE TABLE IF NOT EXISTS app_settings \
                         ( \
                             id \
                             SERIAL \
                             PRIMARY \
                             KEY, \
                             setting_id \
                             VARCHAR \
                         ( \
                             100 \
                         ) UNIQUE NOT NULL,
                             selected_department VARCHAR \
                         ( \
                             100 \
                         ),
                             selected_model VARCHAR \
                         ( \
                             50 \
                         ),
                             updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                      ); \
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
                                                        );
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


def check_document_type_column():
    """promptsテーブルにdocument_typeカラムが存在するか確認し、なければ追加する"""
    try:
        db_manager = DatabaseManager.get_instance()
        engine = db_manager.get_engine()

        # カラム存在確認クエリ
        check_column_query = """
                             SELECT column_name
                             FROM information_schema.columns
                             WHERE table_name = 'prompts' \
                               AND column_name = 'document_type'; \
                             """

        with engine.connect() as conn:
            result = conn.execute(text(check_column_query))
            column_exists = result.fetchone() is not None

            if not column_exists:
                # document_typeカラムを追加
                add_column_query = """
                                   ALTER TABLE prompts
                                       ADD COLUMN document_type VARCHAR(100) DEFAULT '退院時サマリ' NOT NULL; \
                                   """

                # 既存のユニーク制約を削除して再作成
                drop_constraint_query = """
                                        ALTER TABLE prompts DROP CONSTRAINT IF EXISTS unique_prompt; \
                                        """

                create_constraint_query = """
                                          ALTER TABLE prompts
                                              ADD CONSTRAINT unique_prompt
                                                  UNIQUE (department, document_type, doctor, name); \
                                          """

                conn.execute(text(add_column_query))
                conn.execute(text(drop_constraint_query))
                conn.execute(text(create_constraint_query))

                print("promptsテーブルにdocument_typeカラムを追加しました。")

        return True
    except Exception as e:
        raise DatabaseError(f"document_typeカラムの追加中にエラーが発生しました: {str(e)}")


def initialize_database():
    max_retries = 5
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            # まずAlembicマイグレーションを試みる
            migration_success = run_alembic_migrations()

            if not migration_success:
                # マイグレーションが失敗した場合は従来の方法を使用
                create_tables()
                check_document_type_column()

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
