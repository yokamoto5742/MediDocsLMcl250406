import time
from sqlalchemy import text
from database.db import DatabaseManager
from database.schema import initialize_database
from utils.exceptions import DatabaseError

def drop_all_tables():
    db_manager = DatabaseManager.get_instance()
    engine = db_manager.get_engine()

    tables = ['app_settings', 'prompts', 'summary_usage']
    try:
        with engine.begin() as conn:
            conn.execute(text("SET CONSTRAINTS ALL DEFERRED;"))

            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

            print(f"テーブルを削除しました: {', '.join(tables)}")
        return True
    except Exception as e:
        raise DatabaseError(f"テーブル削除中にエラーが発生しました: {str(e)}")


def reset_database():
    max_retries = 5
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            # 1. すべてのテーブルを削除
            drop_all_tables()

            # 2. データベースを初期化（テーブル作成とデフォルトデータの挿入）
            initialize_database()

            print("データベースが正常にリセットされました")
            return True
        except Exception as e:
            last_error = e
            retry_count += 1
            wait_time = 2 ** retry_count  # 指数バックオフ
            print(f"データベースリセットに失敗しました（試行 {retry_count}/{max_retries}）: {str(e)}")
            print(f"{wait_time}秒後に再試行します...")
            time.sleep(wait_time)

    # 全リトライが失敗した場合
    raise DatabaseError(f"データベースのリセットに失敗しました: {str(last_error)}")


if __name__ == "__main__":
    print("データベースのリセットを開始します...")
    reset_database()
    print("データベースのリセットが完了しました。")
