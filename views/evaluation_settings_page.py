import streamlit as st

from services.evaluation_service import create_or_update_evaluation_prompt, get_evaluation_prompt
from ui_components.navigation import change_page
from utils.constants import DOCUMENT_TYPES
from utils.error_handlers import handle_error
from utils.exceptions import AppError


DEFAULT_EVALUATION_PROMPTS = {
    "主治医意見書": """以下の主治医意見書の出力を評価してください。

評価基準:
1. 正確性: 入力情報が正確に反映されているか
2. 完全性: 必要な情報が漏れなく含まれているか
3. 一貫性: 前回の記載との一貫性があるか
4. 文書構造: 適切なセクション分けがされているか
5. 専門性: 医療文書として適切な表現が使用されているか

各評価基準について5段階で評価し、改善点があれば具体的に指摘してください。
""",
    "訪問看護指示書": """以下の訪問看護指示書の出力を評価してください。

評価基準:
1. 正確性: 入力情報が正確に反映されているか
2. 完全性: 訪問看護に必要な指示内容が網羅されているか
3. 一貫性: 前回の記載との一貫性があるか
4. 指示内容の明確性: 看護師が実施すべき内容が明確に記載されているか
5. 専門性: 医療文書として適切な表現が使用されているか

各評価基準について5段階で評価し、改善点があれば具体的に指摘してください。
"""
}


def _render_evaluation_form(document_type: str) -> None:
    """文書種別ごとの評価プロンプトフォームを表示"""
    prompt_data = get_evaluation_prompt(document_type)
    existing_content = prompt_data.get("content", "") if prompt_data else ""

    if not existing_content:
        st.info(f"{document_type}の評価プロンプトが設定されていません。デフォルトプロンプトを参考に設定してください。")

    default_prompt = DEFAULT_EVALUATION_PROMPTS.get(document_type, "")

    with st.form(key=f"evaluation_prompt_form_{document_type}"):
        prompt_content = st.text_area(
            "評価プロンプト",
            value=existing_content if existing_content else default_prompt,
            height=400,
            key=f"evaluation_prompt_content_{document_type}",
            help="評価プロンプトを入力してください"
        )

        submit = st.form_submit_button("保存", type="primary")

        if submit:
            success, message = create_or_update_evaluation_prompt(document_type, prompt_content)
            if success:
                st.session_state.success_message = message
                st.rerun()
            else:
                raise AppError(message)


@handle_error
def evaluation_settings_ui():
    if st.session_state.get("success_message"):
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    if st.button("作成画面に戻る", key="back_to_main_from_evaluation"):
        change_page("main")
        st.rerun()

    tabs = st.tabs(DOCUMENT_TYPES)

    for i, document_type in enumerate(DOCUMENT_TYPES):
        with tabs[i]:
            _render_evaluation_form(document_type)
