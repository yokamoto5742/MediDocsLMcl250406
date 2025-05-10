import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from utils.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER,
    POSTGRES_PASSWORD, POSTGRES_DB
)
from utils.exceptions import DatabaseError


class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance

    def __init__(self):
        if DatabaseManager._engine is not None:
            return

        if not all([POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
            raise DatabaseError("PostgreSQL接続情報が設定されていません。環境変数または設定ファイルを確認してください。")

        try:
            # PostgreSQL接続文字列の作成
            connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

            # SQLAlchemyエンジンの作成
            DatabaseManager._engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600
            )

            # セッションファクトリの作成
            DatabaseManager._session_factory = sessionmaker(bind=DatabaseManager._engine)

            # 接続テスト
            with DatabaseManager._engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        except Exception as e:
            raise DatabaseError(f"PostgreSQLへの接続に失敗しました: {str(e)}")

    @staticmethod
    def get_engine():
        return DatabaseManager._engine

    @staticmethod
    def get_session():
        """新しいSQLAlchemyセッションを取得"""
        if DatabaseManager._session_factory is None:
            raise DatabaseError("データベース接続が初期化されていません")
        return DatabaseManager._session_factory()

    def execute_query(self, query, params=None, fetch=True):
        """
        SQLクエリを実行する汎用メソッド

        Args:
            query (str): 実行するSQLクエリ
            params (dict, optional): クエリパラメータ
            fetch (bool): 結果を取得するかどうか

        Returns:
            list/None: fetch=Trueの場合は結果リスト、そうでなければNone
        """
        session = self.get_session()
        try:
            result = session.execute(text(query), params or {})
            if fetch:
                # SQLAlchemy Rowオブジェクトを正しく辞書に変換
                data = []
                for row in result:
                    # _mapping属性を使用して辞書に変換
                    if hasattr(row, '_mapping'):
                        data.append(dict(row._mapping))
                    else:
                        # 古いバージョンのSQLAlchemy用のフォールバック
                        data.append(dict(zip(row.keys(), row)))
                session.commit()
                return data
            session.commit()
            return None
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"クエリ実行中にエラーが発生しました: {str(e)}")
        finally:
            session.close()


def get_users_collection():
    """ユーザー情報を取得するためのメソッド"""
    try:
        db_manager = DatabaseManager.get_instance()
        query = "SELECT * FROM users"
        return db_manager.execute_query(query)
    except Exception as e:
        raise DatabaseError(f"ユーザー情報の取得に失敗しました: {str(e)}")


def get_usage_collection():
    """使用統計を保存するテーブルからデータを取得"""
    try:
        db_manager = DatabaseManager.get_instance()
        query = "SELECT * FROM summary_usage"
        return db_manager.execute_query(query)
    except Exception as e:
        raise DatabaseError(f"使用状況の取得に失敗しました: {str(e)}")


def get_settings_collection():
    """アプリ設定を取得するためのメソッド"""
    try:
        db_manager = DatabaseManager.get_instance()
        query = "SELECT * FROM app_settings"
        return db_manager.execute_query(query)
    except Exception as e:
        raise DatabaseError(f"設定の取得に失敗しました: {str(e)}")