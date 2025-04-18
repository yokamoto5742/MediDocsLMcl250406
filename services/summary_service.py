import datetime
import streamlit as st
from utils.error_handlers import handle_error
from utils.exceptions import APIError
from utils.claude_api import generate_discharge_summary as claude_generate_discharge_summary
from utils.gemini_api import generate_discharge_summary as gemini_generate_discharge_summary
from utils.text_processor import format_discharge_summary, parse_discharge_summary
from utils.db import get_usage_collection
from utils.config import GEMINI_CREDENTIALS, CLAUDE_API_KEY, GEMINI_MODEL, GEMINI_FLASH_MODEL, MAX_INPUT_TOKENS, MIN_INPUT_TOKENS
from utils.constants import MESSAGES

@handle_error
def process_discharge_summary(input_text):
    if not GEMINI_CREDENTIALS and not CLAUDE_API_KEY:
        raise APIError(MESSAGES["NO_API_CREDENTIALS"])

    if not input_text:
        st.warning(MESSAGES["NO_INPUT"])
        return

    input_length = len(input_text.strip())
    if input_length < MIN_INPUT_TOKENS:
        st.warning(f"{MESSAGES['INPUT_TOO_SHORT']}")
        return

    if input_length > MAX_INPUT_TOKENS:
        st.warning(f"{MESSAGES['INPUT_TOO_LONG']}")
        return

    try:
        with st.spinner("退院時サマリを作成中..."):
            selected_model = getattr(st.session_state, "selected_model",
                                     st.session_state.available_models[
                                         0] if st.session_state.available_models else None)

            if selected_model == "Claude" and CLAUDE_API_KEY:
                discharge_summary, input_tokens, output_tokens = claude_generate_discharge_summary(
                    input_text,
                    st.session_state.selected_department,
                )
                model_detail = selected_model
            elif selected_model == "Gemini_Pro" and GEMINI_MODEL and GEMINI_CREDENTIALS:
                discharge_summary, input_tokens, output_tokens = gemini_generate_discharge_summary(
                    input_text,
                    st.session_state.selected_department,
                    GEMINI_MODEL,
                )
                model_detail = GEMINI_MODEL
            elif selected_model == "Gemini_Flash" and GEMINI_FLASH_MODEL and GEMINI_CREDENTIALS:
                discharge_summary, input_tokens, output_tokens = gemini_generate_discharge_summary(
                    input_text,
                    st.session_state.selected_department,
                    GEMINI_FLASH_MODEL,
                )
                model_detail = GEMINI_FLASH_MODEL
            else:
                raise APIError(MESSAGES["NO_API_CREDENTIALS"])

            discharge_summary = format_discharge_summary(discharge_summary)
            st.session_state.discharge_summary = discharge_summary

            parsed_summary = parse_discharge_summary(discharge_summary)
            st.session_state.parsed_summary = parsed_summary

            usage_collection = get_usage_collection()
            usage_data = {
                "date": datetime.datetime.now(),
                "app_type": "退院時サマリ",
                "model": selected_model,
                "model_detail": model_detail,
                "department": st.session_state.selected_department,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
            usage_collection.insert_one(usage_data)

    except Exception as e:
        raise APIError(f"退院時サマリの作成中にエラーが発生しました: {str(e)}")
