import datetime
from sqlalchemy import text

from database.db import DatabaseManager
from utils.config import get_config
from utils.constants import DEFAULT_DEPARTMENTS, MESSAGES, DEPARTMENT_DOCTORS_MAPPING
from utils.exceptions import DatabaseError, AppError
from database.schema import initialize_database as init_schema
from utils.document_type_manager import initialize_document_types, get_all_document_types


def get_prompt_collection():
    """プロンプトデータを取得するためのメソッド"""
    try:
        db_manager = DatabaseManager.get_instance()
        return db_manager
    except Exception as e:
        raise DatabaseError(f"プロンプトコレクションの取得に失敗しました: {str(e)}")


def get_department_collection():
    """診療科データを取得するためのメソッド"""
    try:
        db_manager = DatabaseManager.get_instance()
        return db_manager
    except Exception as e:
        raise DatabaseError(f"診療科コレクションの取得に失敗しました: {str(e)}")


def get_current_datetime():
    return datetime.datetime.now()


def update_document(collection, query_dict, update_data):
    """
    ドキュメントを更新する

    Args:
        collection: DatabaseManagerのインスタンス
        query_dict: 更新対象を特定するための条件辞書
        update_data: 更新するデータを含む辞書
    """
    try:
        now = get_current_datetime()
        update_data.update({"updated_at": now})

        # query_dictがdepartmentを含む場合はpromptsテーブル
        if "department" in query_dict:
            query = """
                    UPDATE prompts
                    SET name       = :name, \
                        content    = :content, \
                        updated_at = :updated_at
                    WHERE department = :department \
                    """
            params = {
                "name": update_data.get("name"),
                "content": update_data.get("content"),
                "updated_at": update_data["updated_at"],
                "department": query_dict["department"]
            }
        # query_dictがnameを含む場合はdepartmentsテーブル
        elif "name" in query_dict:
            # 更新対象のフィールドだけを含めるように調整
            set_clauses = []
            params = {"name": query_dict["name"], "updated_at": update_data["updated_at"]}

            if "default_model" in update_data:
                set_clauses.append("default_model = :default_model")
                params["default_model"] = update_data["default_model"]

            if "order_index" in update_data:
                set_clauses.append("order_index = :order_index")
                params["order_index"] = update_data["order_index"]

            query = f"""
            UPDATE departments
            SET {', '.join(set_clauses)}, updated_at = :updated_at
            WHERE name = :name
            """
        else:
            raise ValueError("不明な更新条件です")

        collection.execute_query(query, params, fetch=False)
        return True

    except Exception as e:
        raise DatabaseError(f"ドキュメントの更新に失敗しました: {str(e)}")


def initialize_departments():
    """初期診療科データをデータベースに作成"""
    try:
        department_collection = get_department_collection()

        # 診療科の数を確認
        query = "SELECT COUNT(*) as count FROM departments"
        result = department_collection.execute_query(query)
        existing_count = result[0]["count"] if result else 0

        if existing_count == 0:
            for idx, dept in enumerate(DEFAULT_DEPARTMENTS):
                insert_document(department_collection, {
                    "name": dept,
                    "order_index": idx,
                    "default_model": None
                })

    except Exception as e:
        raise DatabaseError(f"診療科の初期化に失敗しました: {str(e)}")


def get_all_departments():
    """すべての診療科名のリストを取得"""
    try:
        department_collection = get_department_collection()
        query = "SELECT name FROM departments ORDER BY order_index"
        result = department_collection.execute_query(query)
        return [dept["name"] for dept in result]
    except Exception as e:
        raise DatabaseError(f"診療科の取得に失敗しました: {str(e)}")


def create_department(name, default_model=None):
    """新しい診療科を作成"""
    try:
        if not name:
            return False, "診療科名を入力してください"

        department_collection = get_department_collection()
        prompt_collection = get_prompt_collection()

        # 既存の診療科を確認
        check_query = "SELECT name FROM departments WHERE name = :name"
        existing = department_collection.execute_query(check_query, {"name": name})

        if existing:
            return False, MESSAGES["DEPARTMENT_EXISTS"]

        # 最大の順序を確認
        max_order_query = "SELECT MAX(order_index) as max_order FROM departments"
        max_order_result = department_collection.execute_query(max_order_query)
        max_order = max_order_result[0]["max_order"] if max_order_result and max_order_result[0][
            "max_order"] is not None else -1
        next_order = max_order + 1

        # 新しい診療科を挿入
        insert_document(department_collection, {
            "name": name,
            "order_index": next_order,
            "default_model": default_model
        })

        # デフォルトプロンプトを取得
        default_prompt_query = "SELECT content FROM prompts WHERE department = 'default' AND document_type = '退院時サマリ' AND doctor = 'default' AND is_default = true"
        default_prompt_result = prompt_collection.execute_query(default_prompt_query)

        if not default_prompt_result:
            config = get_config()
            default_prompt_content = config['PROMPTS']['discharge_summary']
        else:
            default_prompt_content = default_prompt_result[0]["content"]

        # 関連する医師のリスト
        doctors = DEPARTMENT_DOCTORS_MAPPING.get(name, ["default"])
        document_types = get_all_document_types()
        if not document_types:
            document_types = ["退院時サマリ"]

        # 各医師と文書種類の組み合わせでプロンプトを作成
        for doctor in doctors:
            for doc_type in document_types:
                insert_document(prompt_collection, {
                    "department": name,
                    "document_type": doc_type,
                    "doctor": doctor,
                    "name": doc_type,
                    "content": default_prompt_content,
                    "is_default": False
                })

        return True, MESSAGES["DEPARTMENT_CREATED"]
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"診療科の作成中にエラーが発生しました: {str(e)}")


def delete_department(name):
    """診療科を削除"""
    try:
        department_collection = get_department_collection()
        prompt_collection = get_prompt_collection()

        # トランザクション開始
        session = department_collection.get_session()
        try:
            # 診療科を削除
            dept_query = "DELETE FROM departments WHERE name = :name"
            result = session.execute(text(dept_query), {"name": name})
            deleted_count = result.rowcount

            if deleted_count == 0:
                session.rollback()
                return False, "診療科が見つかりません"

            # 関連するプロンプトを削除
            prompt_query = "DELETE FROM prompts WHERE department = :department"
            session.execute(text(prompt_query), {"department": name})

            session.commit()
            return True, "診療科を削除しました"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"診療科の削除中にエラーが発生しました: {str(e)}")


def update_department_order(name, new_order):
    """診療科の表示順序を更新"""
    try:
        department_collection = get_department_collection()

        # 現在の順序を取得
        current_query = "SELECT order_index FROM departments WHERE name = :name"
        current_result = department_collection.execute_query(current_query, {"name": name})

        if not current_result:
            return False, "診療科が見つかりません"

        current_order = current_result[0]["order_index"]

        # トランザクション開始
        session = department_collection.get_session()
        try:
            # 他の診療科の順序を調整
            if new_order > current_order:
                # 順序を下げる場合（他の項目を上に移動）
                shift_query = """
                              UPDATE departments
                              SET order_index = order_index - 1, \
                                  updated_at  = CURRENT_TIMESTAMP
                              WHERE order_index > :current_order \
                                AND order_index <= :new_order \
                              """
                session.execute(text(shift_query), {
                    "current_order": current_order,
                    "new_order": new_order
                })
            else:
                # 順序を上げる場合（他の項目を下に移動）
                shift_query = """
                              UPDATE departments
                              SET order_index = order_index + 1, \
                                  updated_at  = CURRENT_TIMESTAMP
                              WHERE order_index >= :new_order \
                                AND order_index < :current_order \
                              """
                session.execute(text(shift_query), {
                    "current_order": current_order,
                    "new_order": new_order
                })

            # 対象の診療科を更新
            update_query = """
                           UPDATE departments
                           SET order_index = :new_order, \
                               updated_at  = CURRENT_TIMESTAMP
                           WHERE name = :name \
                           """
            session.execute(text(update_query), {
                "name": name,
                "new_order": new_order
            })

            session.commit()
            return True, "診療科の順序を更新しました"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"診療科の順序更新中にエラーが発生しました: {str(e)}")


def get_department_by_name(name):
    """診療科名から診療科情報を取得"""
    try:
        department_collection = get_department_collection()
        query = "SELECT * FROM departments WHERE name = :name"
        result = department_collection.execute_query(query, {"name": name})
        return result[0] if result else None
    except Exception as e:
        raise DatabaseError(f"診療科の取得に失敗しました: {str(e)}")


def update_department(name, default_model):
    """診療科の設定を更新"""
    try:
        department_collection = get_department_collection()
        query = """
                UPDATE departments
                SET default_model = :default_model, \
                    updated_at    = CURRENT_TIMESTAMP
                WHERE name = :name \
                """
        department_collection.execute_query(query, {
            "name": name,
            "default_model": default_model
        }, fetch=False)
        return True, "診療科を更新しました"
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"診療科の更新中にエラーが発生しました: {str(e)}")


def get_all_prompts():
    """すべてのプロンプト情報を取得"""
    try:
        prompt_collection = get_prompt_collection()
        query = "SELECT * FROM prompts ORDER BY department"
        return prompt_collection.execute_query(query)
    except Exception as e:
        raise DatabaseError(f"プロンプト一覧の取得に失敗しました: {str(e)}")


# utils/prompt_manager.pyの一部を修正

def create_or_update_prompt(department, document_type, doctor, name, content):
    """プロンプトを作成または更新"""
    try:
        if not department or not document_type or not doctor or not name or not content:
            return False, "すべての項目を入力してください"

        prompt_collection = get_prompt_collection()

        query = "SELECT * FROM prompts WHERE department = :department AND document_type = :document_type AND doctor = :doctor"
        existing = prompt_collection.execute_query(query, {
            "department": department,
            "document_type": document_type,
            "doctor": doctor
        })

        if existing:
            update_query = """
                           UPDATE prompts
                           SET name       = :name, \
                               content    = :content, \
                               updated_at = CURRENT_TIMESTAMP
                           WHERE department = :department AND document_type = :document_type AND doctor = :doctor \
                           """

            prompt_collection.execute_query(update_query, {
                "department": department,
                "document_type": document_type,
                "doctor": doctor,
                "name": name,
                "content": content
            }, fetch=False)
            return True, "プロンプトを更新しました"
        else:
            insert_document(prompt_collection, {
                "department": department,
                "document_type": document_type,
                "doctor": doctor,
                "name": name,
                "content": content,
                "is_default": False
            })
            return True, "プロンプトを新規作成しました"
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"プロンプトの作成/更新中にエラーが発生しました: {str(e)}")


def delete_prompt(department, document_type, doctor):
    """プロンプトを削除"""
    try:
        if department == "default" and document_type == "退院時サマリ" and doctor == "default":
            return False, "デフォルトプロンプトは削除できません"

        prompt_collection = get_prompt_collection()

        # トランザクション開始
        session = prompt_collection.get_session()
        try:
            # プロンプトを削除
            prompt_query = "DELETE FROM prompts WHERE department = :department AND document_type = :document_type AND doctor = :doctor"
            result = session.execute(text(prompt_query), {
                "department": department,
                "document_type": document_type,
                "doctor": doctor
            })
            deleted_count = result.rowcount

            if deleted_count == 0:
                session.rollback()
                return False, "プロンプトが見つかりません"

            session.commit()
            return True, "プロンプトを削除しました"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        raise AppError(f"プロンプトの削除中にエラーが発生しました: {str(e)}")


def insert_document(collection, document):
    """
    ドキュメントをテーブルに挿入する

    Args:
        collection: DatabaseManagerのインスタンス
        document: 挿入するデータを含む辞書
    """
    try:
        now = get_current_datetime()
        document.update({
            "created_at": now,
            "updated_at": now
        })

        # テーブル名を推測し、適切なSQLを生成
        if "name" in document and "order_index" in document:
            # departmentsテーブルへの挿入
            query = """
                    INSERT INTO departments (name, order_index, default_model, created_at, updated_at)
                    VALUES (:name, :order_index, :default_model, :created_at, :updated_at) RETURNING id; \
                    """
            params = {
                "name": document["name"],
                "order_index": document["order_index"],
                "default_model": document.get("default_model"),
                "created_at": document["created_at"],
                "updated_at": document["updated_at"]
            }
        elif "department" in document:
            # promptsテーブルへの挿入
            query = """
                    INSERT INTO prompts (department, document_type, doctor, name, content, is_default, created_at, updated_at)
                    VALUES (:department, :document_type, :doctor, :name, :content, :is_default, :created_at, :updated_at) RETURNING id; \
                    """
            params = {
                "department": document["department"],
                "document_type": document.get("document_type", "退院時サマリ"),  # デフォルト値を設定
                "doctor": document["doctor"],
                "name": document["name"],
                "content": document["content"],
                "is_default": document.get("is_default", False),
                "created_at": document["created_at"],
                "updated_at": document["updated_at"]
            }
        else:
            raise ValueError("不明なドキュメント形式です")

        result = collection.execute_query(query, params)
        return result[0]["id"] if result else None

    except Exception as e:
        raise DatabaseError(f"ドキュメントの挿入に失敗しました: {str(e)}")


def initialize_default_prompt():
    """デフォルトプロンプトの初期化"""
    try:
        prompt_collection = get_prompt_collection()

        query = "SELECT * FROM prompts WHERE department = 'default' AND document_type = '退院時サマリ' AND doctor = 'default' AND is_default = true"
        default_prompt = prompt_collection.execute_query(query)

        if not default_prompt:
            config = get_config()
            default_prompt_content = config['PROMPTS']['discharge_summary']

            insert_document(prompt_collection, {
                "department": "default",
                "document_type": "退院時サマリ",
                "doctor": "default",
                "name": "退院時サマリ",
                "content": default_prompt_content,
                "is_default": True
            })
    except Exception as e:
        raise DatabaseError(f"デフォルトプロンプトの初期化に失敗しました: {str(e)}")


def get_prompt_by_department(department="default", document_type="退院時サマリ", doctor="default"):
    try:
        prompt_collection = get_prompt_collection()
        query = "SELECT * FROM prompts WHERE department = :department AND document_type = :document_type AND doctor = :doctor"
        prompt = prompt_collection.execute_query(query, {
            "department": department,
            "document_type": document_type,
            "doctor": doctor
        })

        if not prompt:
            # リクエストされた組み合わせが存在しない場合はデフォルトを取得
            default_query = "SELECT * FROM prompts WHERE department = 'default' AND document_type = '退院時サマリ' AND doctor = 'default' AND is_default = true"
            prompt = prompt_collection.execute_query(default_query)

        return prompt[0] if prompt else None
    except Exception as e:
        raise DatabaseError(f"プロンプトの取得に失敗しました: {str(e)}")


def initialize_database():
    """データベースの初期化を行う"""
    try:
        init_schema()

        initialize_default_prompt()
        initialize_departments()
        initialize_document_types()

        # 各診療科と医師の組み合わせでデフォルトプロンプトを初期化
        prompt_collection = get_prompt_collection()
        config = get_config()
        default_prompt_content = config['PROMPTS']['discharge_summary']

        departments = get_all_departments()
        document_types = get_all_document_types()

        for dept in departments:
            doctors = DEPARTMENT_DOCTORS_MAPPING.get(dept, ["default"])
            for doctor in doctors:
                for doc_type in document_types:
                    # プロンプトが存在するか確認
                    check_query = """
                                  SELECT * \
                                  FROM prompts
                                  WHERE department = :department
                                    AND document_type = :document_type
                                    AND doctor = :doctor \
                                  """
                    existing = prompt_collection.execute_query(check_query, {
                        "department": dept,
                        "document_type": doc_type,
                        "doctor": doctor
                    })

                    if not existing:
                        # プロンプトが存在しなければ作成
                        insert_document(prompt_collection, {
                            "department": dept,
                            "document_type": doc_type,
                            "doctor": doctor,
                            "name": doc_type,
                            "content": default_prompt_content,
                            "is_default": False
                        })

        # 順序が設定されていない診療科の処理
        department_collection = get_department_collection()
        query = "SELECT * FROM departments WHERE order_index IS NULL"
        departments_without_order = department_collection.execute_query(query)

        if departments_without_order:
            # 最大の順序を確認
            max_order_query = "SELECT MAX(order_index) as max_order FROM departments WHERE order_index IS NOT NULL"
            max_order_result = department_collection.execute_query(max_order_query)
            next_order = max_order_result[0]["max_order"] + 1 if max_order_result and max_order_result[0][
                "max_order"] is not None else 0

            # 順序を設定
            for dept in departments_without_order:
                update_query = """
                               UPDATE departments
                               SET order_index = :order_index, \
                                   updated_at  = CURRENT_TIMESTAMP
                               WHERE id = :id \
                               """
                department_collection.execute_query(update_query, {
                    "id": dept["id"],
                    "order_index": next_order
                }, fetch=False)
                next_order += 1

    except Exception as e:
        raise DatabaseError(f"データベースの初期化に失敗しました: {str(e)}")