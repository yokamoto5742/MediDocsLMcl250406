import streamlit as st

from services.summary_service import process_summary
from utils.constants import MESSAGES, TAB_NAMES
from utils.error_handlers import handle_error
from ui_components.navigation import render_sidebar


def clear_inputs():
    st.session_state.input_text = ""
    st.session_state.additional_info = "【前回の記載】\n(ここに貼り付け)"
    st.session_state.output_summary = ""
    st.session_state.parsed_summary = {}
    st.session_state.summary_generation_time = None
    st.session_state.clear_input = True

    for key in list(st.session_state.keys()):
        if key.startswith("input_text"):
            st.session_state[key] = ""


def render_input_section():
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False

    if "additional_info" not in st.session_state:
        st.session_state.additional_info = "【前回の記載】\n(ここに貼り付け)"

    input_text = st.text_area(
        "カルテ記載入力",
        height=100,
        placeholder="ここを右クリックしてテキストを貼り付けてください...",
        key="input_text"
    )

    additional_info = st.text_area(
        "追加情報入力",
        height=100,
        key="additional_info"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("作成", type="primary"):
            process_summary(input_text, additional_info)

    with col2:
        if st.button("テキストをクリア", on_click=clear_inputs):
            pass


def render_summary_results():
    if st.session_state.output_summary:
        if st.session_state.parsed_summary:
            tabs = st.tabs([
                TAB_NAMES["ALL"], TAB_NAMES["TREATMENT"], TAB_NAMES["SPECIAL"], TAB_NAMES["NOTE"]])

            with tabs[0]:
                st.code(st.session_state.output_summary,
                        language=None,
                        height=150
                        )

            sections = [TAB_NAMES["TREATMENT"], TAB_NAMES["SPECIAL"], TAB_NAMES["NOTE"]]
            for i, section in enumerate(sections, 1):
                with tabs[i]:
                    section_content = st.session_state.parsed_summary.get(section, "")
                    st.code(section_content,
                            language=None,
                            height=150)

        st.info(MESSAGES["COPY_INSTRUCTION"])

        if "summary_generation_time" in st.session_state and st.session_state.summary_generation_time is not None:
            processing_time = st.session_state.summary_generation_time
            st.info(MESSAGES["PROCESSING_TIME"].format(processing_time=processing_time))


@handle_error
def main_page_app():
    render_sidebar()
    render_input_section()
    render_summary_results()
