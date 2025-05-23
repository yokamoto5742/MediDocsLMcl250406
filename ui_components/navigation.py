import streamlit as st

from database.db import DatabaseManager
from utils.config import GEMINI_MODEL, GEMINI_CREDENTIALS, GEMINI_FLASH_MODEL, CLAUDE_API_KEY, OPENAI_API_KEY
from utils.constants import DEFAULT_DEPARTMENTS, DEFAULT_DOCUMENT_TYPES, DEPARTMENT_DOCTORS_MAPPING
from utils.prompt_manager import get_prompt_by_department


def change_page(page):
    st.session_state.current_page = page


def update_document_model():
    selected_dept = st.session_state.selected_department
    selected_doctor = st.session_state.selected_doctor
    new_doc_type = st.session_state.document_type_selector

    st.session_state.selected_document_type = new_doc_type
    st.session_state.model_explicitly_selected = False

    prompt_data = get_prompt_by_department(selected_dept, new_doc_type, selected_doctor)
    if prompt_data and prompt_data.get("selected_model") in st.session_state.available_models:
        st.session_state.selected_model = prompt_data.get("selected_model")
    elif "available_models" in st.session_state and st.session_state.available_models:
        if "Gemini_Pro" in st.session_state.available_models:
            st.session_state.selected_model = "Gemini_Pro"
        else:
            st.session_state.selected_model = st.session_state.available_models[0]


def render_sidebar():
    departments = ["default"] + DEFAULT_DEPARTMENTS

    previous_dept = st.session_state.selected_department
    previous_model = getattr(st.session_state, "selected_model", None)
    previous_doctor = getattr(st.session_state, "selected_doctor", None)

    try:
        index = departments.index(st.session_state.selected_department)
    except ValueError:
        index = 0
        st.session_state.selected_department = departments[0]

    # 1. 診療科を最初に表示（選択肢が複数ある場合のみ）
    if len(departments) > 1:
        selected_dept = st.sidebar.selectbox(
            "診療科",
            departments,
            index=index,
            format_func=lambda x: "全科共通" if x == "default" else x,
            key="department_selector"
        )
        st.session_state.selected_department = selected_dept
    else:
        # 選択肢が1つしかない場合は自動選択
        st.session_state.selected_department = departments[0]
        selected_dept = departments[0]

    # 2. 医師名を次に表示（選択肢が複数ある場合のみ）
    available_doctors = DEPARTMENT_DOCTORS_MAPPING.get(selected_dept, ["default"])

    if "selected_doctor" not in st.session_state or st.session_state.selected_doctor not in available_doctors:
        st.session_state.selected_doctor = available_doctors[0]

    if selected_dept != previous_dept:
        if selected_dept == "default":
            st.session_state.model_explicitly_selected = False
            if "Gemini_Pro" in st.session_state.available_models:
                st.session_state.selected_model = "Gemini_Pro"
            elif st.session_state.available_models:
                st.session_state.selected_model = st.session_state.available_models[0]
            st.session_state.selected_doctor = "default"
        else:
            st.session_state.selected_doctor = available_doctors[0]
            st.session_state.model_explicitly_selected = False

        save_user_settings(selected_dept, st.session_state.selected_model, st.session_state.selected_doctor)
        st.rerun()

    if len(available_doctors) > 1:
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
    else:
        # 選択肢が1つしかない場合は自動選択
        st.session_state.selected_doctor = available_doctors[0]
        selected_doctor = available_doctors[0]

    # 3. 文書名を次に表示（選択肢が複数ある場合のみ）
    document_types = DEFAULT_DOCUMENT_TYPES

    if not document_types:
        document_types = ["主治医意見書"]

    if "selected_document_type" not in st.session_state:
        st.session_state.selected_document_type = document_types[0] if document_types else "主治医意見書"

    if len(document_types) > 1:
        selected_document_type = st.sidebar.selectbox(
            "文書名",
            document_types,
            index=document_types.index(
                st.session_state.selected_document_type) if st.session_state.selected_document_type in document_types else 0,
            key="document_type_selector",
            on_change=update_document_model
        )
    else:
        # 選択肢が1つしかない場合は自動選択
        st.session_state.selected_document_type = document_types[0]
        selected_document_type = document_types[0]

    # 4. AIモデル関連の初期化
    st.session_state.available_models = []
    if GEMINI_MODEL and GEMINI_CREDENTIALS:
        st.session_state.available_models.append("Gemini_Pro")
    if GEMINI_FLASH_MODEL and GEMINI_CREDENTIALS:
        st.session_state.available_models.append("Gemini_Flash")
    if CLAUDE_API_KEY:
        st.session_state.available_models.append("Claude")
    if OPENAI_API_KEY:
        st.session_state.available_models.append("GPT4.1")

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
            st.session_state.model_explicitly_selected = True
            save_user_settings(st.session_state.selected_department, st.session_state.selected_model,
                               st.session_state.selected_doctor)

    elif len(st.session_state.available_models) == 1:
        st.session_state.selected_model = st.session_state.available_models[0]
        st.session_state.model_explicitly_selected = False

    st.sidebar.markdown("・入力および出力テキストは保存されません")
    st.sidebar.markdown("・出力結果は必ず確認してください")

    if st.sidebar.button("プロンプト管理", key="sidebar_prompt_management"):
        change_page("prompt_edit")
        st.rerun()

    if st.sidebar.button("統計情報", key="sidebar_usage_statistics"):
        change_page("statistics")
        st.rerun()


def save_user_settings(department, model, doctor="default"):
    try:
        if department != "default" and department not in DEFAULT_DEPARTMENTS:
            department = "default"
        db_manager = DatabaseManager.get_instance()

        check_query = "SELECT * FROM app_settings WHERE setting_id = 'user_preferences'"
        existing = db_manager.execute_query(check_query)

        if existing:
            query = """
                    UPDATE app_settings
                    SET selected_department = :department, \
                        selected_model      = :model, \
                        selected_doctor     = :doctor, \
                        updated_at          = CURRENT_TIMESTAMP
                    WHERE setting_id = 'user_preferences' \
                    """
        else:
            query = """
                    INSERT INTO app_settings (setting_id, selected_department, selected_model, selected_doctor, \
                                              updated_at)
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
    try:
        db_manager = DatabaseManager.get_instance()
        query = "SELECT selected_department, selected_model, selected_doctor FROM app_settings WHERE setting_id = 'user_preferences'"
        settings = db_manager.execute_query(query)

        if settings:
            return settings[0]["selected_department"], settings[0]["selected_model"], settings[0].get("selected_doctor",
                                                                                                      "default")
        return None, None, None
    except Exception as e:
        print(f"設定の読み込みに失敗しました: {str(e)}")
        return None, None, None
