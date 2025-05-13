import datetime
from sqlalchemy import text

from database.db import DatabaseManager
from utils.constants import DEFAULT_DOCUMENT_TYPES
from utils.exceptions import DatabaseError, AppError


def get_document_type_collection():
    """文書種類データを取得するためのメソッド"""
    try:
        db_manager = DatabaseManager.get_instance()
        return db_manager
    except Exception as e:
        raise DatabaseError(f"文書種類コレクションの取得に失敗しました: {str(e)}")


def initialize_document_types():
    """初期文書種類データをデータベースに作成"""
    try:
        doc_type_collection = get_document_type_collection()

        # 文書種類の数を確認
        query = "SELECT COUNT(*) as count FROM document_types"
        result = doc_type_collection.execute_query(query)
        existing_count = result[0]["count"] if result else 0

        if existing_count == 0:
            for idx, doc_type in enumerate(DEFAULT_DOCUMENT_TYPES):
                # 新しい文書種類を挿入
                query = """
                        INSERT INTO document_types (name, order_index, created_at, updated_at)
                        VALUES (:name, :order_index, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """
                doc_type_collection.execute_query(query, {
                    "name": doc_type,
                    "order_index": idx
                }, fetch=False)

    except Exception as e:
        raise DatabaseError(f"文書種類の初期化に失敗しました: {str(e)}")


def get_all_document_types():
    """すべての文書種類名のリストを取得"""
    try:
        doc_type_collection = get_document_type_collection()
        query = "SELECT name FROM document_types ORDER BY order_index"
        result = doc_type_collection.execute_query(query)
        return [doc_type["name"] for doc_type in result]
    except Exception as e:
        raise DatabaseError(f"文書種類の取得に失敗しました: {str(e)}")


def create_document_type(name):
    """新しい文書種類を作成"""
    try:
        if not name:
            return False, "文書種類名を入力してください"

        doc_type_collection = get_document_type_collection()

        # 既存の文書種類を確認
        check_query = "SELECT name FROM document_types WHERE name = :name"
        existing = doc_type_collection.execute_query(check_query, {"name": name})

        if existing:
            return False, "この文書種類は既に存在します"

        # 最大の順序を確認
        max_order_query = "SELECT MAX(order_index) as max_order FROM document_types"
        max_order_result = doc_type_collection.execute_query(max_order_query)
        max_order = max_order_result[0]["max_order"] if max_order_result and max_order_result[0][
            "max_order"] is not None else -1
        next_order = max_order + 1

        # 新しい文書種類を挿入
        query = """
                INSERT INTO document_types (name, order_index, created_at, updated_at)
                VALUES (:name, :order_index, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
        doc_type_collection.execute_query(query, {
            "name": name,
            "order_index": next_order
        }, fetch=False)

        return True, "文書種類を登録しました"
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"文書種類の作成中にエラーが発生しました: {str(e)}")


def delete_document_type(name):
    """文書種類を削除"""
    try:
        doc_type_collection = get_document_type_collection()

        # 文書種類を削除
        query = "DELETE FROM document_types WHERE name = :name"
        result = doc_type_collection.execute_query(query, {"name": name}, fetch=False)

        return True, "文書種類を削除しました"
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"文書種類の削除中にエラーが発生しました: {str(e)}")


def update_document_type_order(name, new_order):
    """文書種類の表示順序を更新"""
    try:
        doc_type_collection = get_document_type_collection()

        # 現在の順序を取得
        current_query = "SELECT order_index FROM document_types WHERE name = :name"
        current_result = doc_type_collection.execute_query(current_query, {"name": name})

        if not current_result:
            return False, "文書種類が見つかりません"

        current_order = current_result[0]["order_index"]

        # トランザクション開始
        session = doc_type_collection.get_session()
        try:
            # 他の文書種類の順序を調整
            if new_order > current_order:
                # 順序を下げる場合（他の項目を上に移動）
                shift_query = """
                              UPDATE document_types
                              SET order_index = order_index - 1,
                                  updated_at  = CURRENT_TIMESTAMP
                              WHERE order_index > :current_order
                                AND order_index <= :new_order
                              """
                session.execute(text(shift_query), {
                    "current_order": current_order,
                    "new_order": new_order
                })
            else:
                # 順序を上げる場合（他の項目を下に移動）
                shift_query = """
                              UPDATE document_types
                              SET order_index = order_index + 1,
                                  updated_at  = CURRENT_TIMESTAMP
                              WHERE order_index >= :new_order
                                AND order_index < :current_order
                              """
                session.execute(text(shift_query), {
                    "current_order": current_order,
                    "new_order": new_order
                })

            # 対象の文書種類を更新
            update_query = """
                           UPDATE document_types
                           SET order_index = :new_order,
                               updated_at  = CURRENT_TIMESTAMP
                           WHERE name = :name
                           """
            session.execute(text(update_query), {
                "name": name,
                "new_order": new_order
            })

            session.commit()
            return True, "文書種類の順序を更新しました"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"文書種類の順序更新中にエラーが発生しました: {str(e)}")
