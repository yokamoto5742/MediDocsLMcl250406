import streamlit as st

from database.db import DatabaseManager
from utils.config import GEMINI_MODEL, GEMINI_CREDENTIALS, GEMINI_FLASH_MODEL, CLAUDE_API_KEY, OPENAI_API_KEY
from utils.prompt_manager import get_all_departments, get_department_by_name
from utils.document_type_manager import get_all_document_types
from utils.constants import DEPARTMENT_DOCTORS_MAPPING


def change_page(page):
    st.session_state.current_page = page


def render_sidebar():
    departments = ["default"] + get_all_departments()

    previous_dept = st.session_state.selected_department
    previous_model = getattr(st.session_state, "selected_model", None)
    previous_doctor = getattr(st.session_state, "selected_doctor", None)

    try:
        index = departments.index(st.session_state.selected_department)
    except ValueError:
        index = 0
        st.session_state.selected_department = departments[0]

    document_types = get_all_document_types()

    if not document_types:
        document_types = ["退院時サマリ"]

    if "selected_document_type" not in st.session_state:
        st.session_state.selected_document_type = document_types[0] if document_types else "退院時サマリ"

    selected_document_type = st.sidebar.selectbox(
        "文書名",
        document_types,
        index=document_types.index(
            st.session_state.selected_document_type) if st.session_state.selected_document_type in document_types else 0
    )

    st.session_state.selected_document_type = selected_document_type

    selected_dept = st.sidebar.selectbox(
        "診療科",
        departments,
        index=index,
        format_func=lambda x: "全科共通" if x == "default" else x,
        key="department_selector"
    )

    st.session_state.available_models = []
    if GEMINI_MODEL and GEMINI_CREDENTIALS:
        st.session_state.available_models.append("Gemini_Pro")
    if GEMINI_FLASH_MODEL and GEMINI_CREDENTIALS:
        st.session_state.available_models.append("Gemini_Flash")
    if CLAUDE_API_KEY:
        st.session_state.available_models.append("Claude")
    if OPENAI_API_KEY:
        st.session_state.available_models.append("GPT4.1")

    st.session_state.selected_department = selected_dept

    available_doctors = DEPARTMENT_DOCTORS_MAPPING.get(selected_dept, ["default"])

    if "selected_doctor" not in st.session_state or st.session_state.selected_doctor not in available_doctors:
        st.session_state.selected_doctor = available_doctors[0]

    if selected_dept != previous_dept:
        if selected_dept == "default":
            if "Gemini_Pro" in st.session_state.available_models:
                st.session_state.selected_model = "Gemini_Pro"
            elif st.session_state.available_models:
                st.session_state.selected_model = st.session_state.available_models[0]
            st.session_state.selected_doctor = "default"
        else:
            dept_data = get_department_by_name(selected_dept)
            if dept_data and "default_model" in dept_data and dept_data["default_model"]:
                if dept_data["default_model"] in st.session_state.available_models:
                    st.session_state.selected_model = dept_data["default_model"]
            st.session_state.selected_doctor = available_doctors[0]

        save_user_settings(selected_dept, st.session_state.selected_model, st.session_state.selected_doctor)
        st.rerun()

    selected_doctor = st.sidebar.selectbox(
        "医師名",
        available_doctors,
        index=available_doctors.index(st.session_state.selected_doctor),
        format_func=lambda x: "医師共通" if x == "default" else x,
        key="doctor_selector"
    )

    if selected_doctor != previous_doctor:
        st.session_state.selected_doctor = selected_doctor
        save_user_settings(st.session_state.selected_department, st.session_state.selected_model, selected_doctor)

    if len(st.session_state.available_models) > 1:
        if "selected_model" not in st.session_state:
            if "Gemini_Pro" in st.session_state.available_models:
                default_model = "Gemini_Pro"
            else:
                default_model = st.session_state.available_models[0]
            st.session_state.selected_model = default_model

        try:
            model_index = st.session_state.available_models.index(st.session_state.selected_model)
        except (ValueError, AttributeError):
            model_index = 0
            if st.session_state.available_models:
                st.session_state.selected_model = st.session_state.available_models[0]

        selected_model = st.sidebar.selectbox(
            "AIモデル",
            st.session_state.available_models,
            index=model_index,
            key="model_selector"
        )

        if selected_model != previous_model:
            st.session_state.selected_model = selected_model
            save_user_settings(st.session_state.selected_department, st.session_state.selected_model, st.session_state.selected_doctor)

    elif len(st.session_state.available_models) == 1:
        st.session_state.selected_model = st.session_state.available_models[0]

    st.sidebar.markdown("・入力および出力テキストは保存されません")
    st.sidebar.markdown("・出力結果は必ず確認してください")

    if st.sidebar.button("診療科管理", key="sidebar_department_management"):
        change_page("department_edit")
        st.rerun()
    if st.sidebar.button("文書種類管理", key="sidebar_document_type_management"):
        change_page("document_type_edit")
        st.rerun()

    if st.sidebar.button("プロンプト管理", key="sidebar_prompt_management"):
        change_page("prompt_edit")
        st.rerun()

    if st.sidebar.button("統計情報", key="sidebar_usage_statistics"):
        change_page("statistics")
        st.rerun()


def save_user_settings(department, model, doctor="default"):
    """ユーザー設定をデータベースに保存"""
    try:
        # DatabaseManagerインスタンスを正しく取得
        db_manager = DatabaseManager.get_instance()

        # 以前の設定を確認
        check_query = "SELECT * FROM app_settings WHERE setting_id = 'user_preferences'"
        existing = db_manager.execute_query(check_query)

        if existing:
            # 更新
            query = """
                    UPDATE app_settings
                    SET selected_department = :department, \
                        selected_model      = :model, \
                        selected_doctor     = :doctor, \
                        updated_at          = CURRENT_TIMESTAMP
                    WHERE setting_id = 'user_preferences' \
                    """
        else:
            # 新規作成
            query = """
                    INSERT INTO app_settings (setting_id, selected_department, selected_model, selected_doctor, updated_at)
                    VALUES ('user_preferences', :department, :model, :doctor, CURRENT_TIMESTAMP) \
                    """

        db_manager.execute_query(query, {
            "department": department,
            "model": model,
            "doctor": doctor
        }, fetch=False)

    except Exception as e:
        print(f"設定の保存に失敗しました: {str(e)}")


def load_user_settings():
    """ユーザー設定をデータベースから読み込み"""
    try:
        db_manager = DatabaseManager.get_instance()
        query = "SELECT selected_department, selected_model, selected_doctor FROM app_settings WHERE setting_id = 'user_preferences'"
        settings = db_manager.execute_query(query)

        if settings:
            return settings[0]["selected_department"], settings[0]["selected_model"], settings[0].get("selected_doctor", "default")
        return None, None, None
    except Exception as e:
        print(f"設定の読み込みに失敗しました: {str(e)}")
        return None, None, None
