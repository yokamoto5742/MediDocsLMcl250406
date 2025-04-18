import streamlit as st
from utils.auth import login_ui, require_login, check_ip_access
from utils.config import REQUIRE_LOGIN, IP_CHECK_ENABLED, IP_WHITELIST
from utils.env_loader import load_environment_variables
from utils.error_handlers import handle_error
from utils.prompt_manager import initialize_database
from screens.department_management import department_management_ui
from screens.prompt_management import prompt_management_ui
from screens.statistics import usage_statistics_ui
from screens.main import main_app as main_page_app

load_environment_variables()
initialize_database()
require_login_setting = REQUIRE_LOGIN

st.set_page_config(
    page_title="退院時サマリ作成アプリ",
    page_icon="📋",
    layout="wide"
)

# セッション状態の初期化
if "discharge_summary" not in st.session_state:
    st.session_state.discharge_summary = ""
if "parsed_summary" not in st.session_state:
    st.session_state.parsed_summary = {}
if "show_password_change" not in st.session_state:
    st.session_state.show_password_change = False
if "selected_department" not in st.session_state:
    st.session_state.selected_department = "default"
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "available_models" not in st.session_state:
    st.session_state.available_models = []

@handle_error
def main_app():
    if st.session_state.current_page == "prompt_edit":
        prompt_management_ui()
        return
    elif st.session_state.current_page == "department_edit":
        department_management_ui()
        return
    elif st.session_state.current_page == "statistics":
        usage_statistics_ui()
        return

    main_page_app()

@handle_error
def main():
    if IP_CHECK_ENABLED:
        if not check_ip_access(IP_WHITELIST):
            st.stop()

    if require_login_setting:
        if require_login():
            main_app()
    else:
        main_app()

if __name__ == "__main__":
    main()
