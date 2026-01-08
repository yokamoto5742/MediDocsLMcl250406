import streamlit as st

from services.evaluation_service import create_or_update_evaluation_prompt, get_evaluation_prompt
from ui_components.navigation import change_page
from utils.error_handlers import handle_error
from utils.exceptions import AppError


DEFAULT_EVALUATION_PROMPT = """以下の医療文書生成の出力を評価してください。

評価基準:
1. 正確性: 入力情報が正確に反映されているか
2. 完全性: 必要な情報が漏れなく含まれているか
3. 一貫性: 前回の記載との一貫性があるか
4. 文書構造: 適切なセクション分けがされているか
5. 専門性: 医療文書として適切な表現が使用されているか

各評価基準について5段階で評価し、改善点があれば具体的に指摘してください。
"""


@handle_error
def evaluation_settings_ui():
    """評価プロンプト設定ページ"""
    if st.session_state.get("success_message"):
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    if st.button("作成画面に戻る", key="back_to_main_from_evaluation"):
        change_page("main")
        st.rerun()

    st.header("出力評価設定")
    st.markdown("生成された出力を評価するためのプロンプトを設定します。")

    prompt_data = get_evaluation_prompt()
    existing_content = prompt_data.get("content", "") if prompt_data else ""

    if not existing_content:
        st.info("評価プロンプトが設定されていません。以下のデフォルトプロンプトを参考に設定してください。")

    with st.form(key="evaluation_prompt_form"):
        prompt_content = st.text_area(
            "評価プロンプト",
            value=existing_content if existing_content else DEFAULT_EVALUATION_PROMPT,
            height=400,
            key="evaluation_prompt_content",
            help="生成出力の評価に使用するプロンプトを入力してください"
        )

        st.markdown("""
**評価時に自動で追加される情報:**
- 【前回の記載】: 前回の文書内容
- 【カルテ記載】: 入力されたカルテ情報
- 【追加情報】: 追加で入力された情報
- 【生成された出力】: 評価対象の生成文書
        """)

        submit = st.form_submit_button("保存", type="primary")

        if submit:
            success, message = create_or_update_evaluation_prompt(prompt_content)
            if success:
                st.session_state.success_message = message
                st.rerun()
            else:
                raise AppError(message)
