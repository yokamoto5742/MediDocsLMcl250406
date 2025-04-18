import streamlit as st
from utils.error_handlers import handle_error
from services.summary_service import process_discharge_summary
from utils.text_processor import parse_discharge_summary
from components.navigation import render_sidebar

def clear_inputs():
    st.session_state.input_text = ""
    st.session_state.discharge_summary = ""
    st.session_state.parsed_summary = {}
    st.session_state.clear_input = True

    for key in list(st.session_state.keys()):
        if key.startswith("input_text"):
            st.session_state[key] = ""

def render_input_section():
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False

    input_text = st.text_area(
        "カルテ情報入力",
        height=100,
        placeholder="ここを右クリックしてテキストを貼り付けてください...",
        key="input_text"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("退院時サマリ作成", type="primary"):
            process_discharge_summary(input_text)

    with col2:
        if st.button("テキストをクリア", on_click=clear_inputs):
            pass

def render_summary_results():
    if st.session_state.discharge_summary:
        if st.session_state.parsed_summary:
            tabs = st.tabs([
                "全文", "入院期間", "現病歴", "入院時検査",
                "入院中の治療経過", "退院申し送り", "禁忌/アレルギー"
            ])

            with tabs[0]:
                st.subheader("全文")
                st.code(st.session_state.discharge_summary,
                        language=None,
                        height=150
                        )

            sections = ["入院期間", "現病歴", "入院時検査", "入院中の治療経過", "退院申し送り", "禁忌/アレルギー"]
            for i, section in enumerate(sections, 1):
                with tabs[i]:
                    section_content = st.session_state.parsed_summary.get(section, "")
                    st.subheader(section)
                    st.code(section_content,
                            language=None,
                            height=150
                            )

        st.info("💡 テキストエリアの右上にマウスを合わせて左クリックでコピーできます")

@handle_error
def main_app():
    render_sidebar()
    render_input_section()
    render_summary_results()
