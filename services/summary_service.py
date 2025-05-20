import datetime
import queue
import threading
import time

import pytz
import streamlit as st

from database.db import DatabaseManager
from external_service.claude_api import claude_generate_summary
from external_service.gemini_api import gemini_generate_summary
from external_service.openai_api import openai_generate_summary
from utils.config import CLAUDE_API_KEY, GEMINI_CREDENTIALS, GEMINI_FLASH_MODEL, GEMINI_MODEL, MAX_INPUT_TOKENS, \
    MIN_INPUT_TOKENS, OPENAI_API_KEY, MAX_TOKEN_THRESHOLD
from utils.constants import APP_TYPE, MESSAGES, DEFAULT_DEPARTMENTS, DEFAULT_DOCUMENT_TYPES
from utils.error_handlers import handle_error
from utils.exceptions import APIError
from utils.prompt_manager import get_prompt_by_department
from utils.text_processor import format_discharge_summary, parse_discharge_summary

JST = pytz.timezone('Asia/Tokyo')


def generate_summary_task(input_text, selected_department, selected_model, result_queue, additional_info="",
                          selected_document_type="主治医意見書", selected_doctor="default", model_explicitly_selected=False):
    try:
        if selected_department != "default" and selected_department not in DEFAULT_DEPARTMENTS:
            selected_department = "default"
        if selected_document_type not in DEFAULT_DOCUMENT_TYPES:
            selected_document_type = DEFAULT_DOCUMENT_TYPES[0]

        # プロンプトデータからモデルを取得
        prompt_data = get_prompt_by_department(selected_department, selected_document_type, selected_doctor)
        prompt_selected_model = prompt_data.get("selected_model") if prompt_data else None

        # ユーザーが明示的にモデルを選択していない場合は、プロンプトに設定されたモデルを使用
        if prompt_selected_model and not model_explicitly_selected:
            selected_model = prompt_selected_model

        estimated_tokens = len(input_text) + len(additional_info or "")
        original_model = selected_model
        model_switched = False

        if estimated_tokens > MAX_TOKEN_THRESHOLD:
            if GEMINI_CREDENTIALS and GEMINI_MODEL:
                if selected_model != "Gemini_Pro":
                    selected_model = "Gemini_Pro"
                    model_switched = True
            elif not GEMINI_CREDENTIALS:
                raise APIError("TOKEN_THRESHOLD_EXCEEDED_NO_GEMINI")

        match selected_model:
            case "Claude" if CLAUDE_API_KEY:
                discharge_summary, input_tokens, output_tokens = claude_generate_summary(
                    input_text,
                    additional_info,
                    selected_department,
                    selected_document_type,
                    selected_doctor
                )
                model_detail = selected_model

            case "Gemini_Pro" if GEMINI_MODEL and GEMINI_CREDENTIALS:
                discharge_summary, input_tokens, output_tokens = gemini_generate_summary(
                    input_text,
                    additional_info,
                    selected_department,
                    selected_document_type,
                    selected_doctor,
                    GEMINI_MODEL,
                )
                model_detail = GEMINI_MODEL

            case "Gemini_Flash" if GEMINI_FLASH_MODEL and GEMINI_CREDENTIALS:
                discharge_summary, input_tokens, output_tokens = gemini_generate_summary(
                    input_text,
                    additional_info,
                    selected_department,
                    selected_document_type,
                    selected_doctor,
                    GEMINI_FLASH_MODEL,
                )
                model_detail = GEMINI_FLASH_MODEL

            case "GPT4.1" if OPENAI_API_KEY:
                try:
                    discharge_summary, input_tokens, output_tokens = openai_generate_summary(
                        input_text,
                        additional_info,
                        selected_department,
                        selected_document_type,
                        selected_doctor,
                    )
                    model_detail = selected_model
                except Exception as e:
                    error_str = str(e)
                    if "insufficient_quota" in error_str or "exceeded your current quota" in error_str:
                        raise APIError(
                            "OpenAI APIのクォータを超過しています。請求情報を確認するか、管理者に連絡してください。")
                    else:
                        raise e

            case _:
                raise APIError(MESSAGES["NO_API_CREDENTIALS"])

        discharge_summary = format_discharge_summary(discharge_summary)
        parsed_summary = parse_discharge_summary(discharge_summary)

        result_queue.put({
            "success": True,
            "discharge_summary": discharge_summary,
            "parsed_summary": parsed_summary,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model_detail": model_detail,
            "model_switched": model_switched,
            "original_model": original_model if model_switched else None
        })

    except Exception as e:
        result_queue.put({"success": False, "error": e})


@handle_error
def process_summary(input_text, additional_info=""):
    if not GEMINI_CREDENTIALS and not CLAUDE_API_KEY and not OPENAI_API_KEY:
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
        start_time = datetime.datetime.now()
        status_placeholder = st.empty()
        result_queue = queue.Queue()

        available_models = getattr(st.session_state, "available_models", [])
        selected_model = getattr(st.session_state, "selected_model",
                                 available_models[0] if available_models else None)
        selected_department = getattr(st.session_state, "selected_department", "default")
        selected_document_type = getattr(st.session_state, "selected_document_type", "退院時サマリ")
        selected_doctor = getattr(st.session_state, "selected_doctor", "default")
        model_explicitly_selected = getattr(st.session_state, "model_explicitly_selected", False)

        summary_thread = threading.Thread(
            target=generate_summary_task,
            args=(
                input_text,
                selected_department,
                selected_model,
                result_queue,
                additional_info,
                selected_document_type,
                selected_doctor,
                model_explicitly_selected
            ),
        )
        summary_thread.start()
        elapsed_time = 0

        with st.spinner("サマリ作成中..."):
            status_placeholder.text(f"⏱️ 経過時間: {elapsed_time}秒")
            while summary_thread.is_alive():
                time.sleep(1)
                elapsed_time = int((datetime.datetime.now() - start_time).total_seconds())
                status_placeholder.text(f"⏱️ 経過時間: {elapsed_time}秒")

        summary_thread.join()
        status_placeholder.empty()
        result = result_queue.get()

        if result["success"]:
            st.session_state.discharge_summary = result["discharge_summary"]
            st.session_state.parsed_summary = result["parsed_summary"]

            input_tokens = result["input_tokens"]
            output_tokens = result["output_tokens"]
            model_detail = result["model_detail"]
            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            st.session_state.summary_generation_time = processing_time

            # モデルが自動切り替えされた場合に通知
            if result.get("model_switched"):
                st.info(
                    f"⚠️ 入力テキストが長いため、自動的に {result['original_model']} から Gemini_Pro に切り替えました。")

            try:
                db_manager = DatabaseManager.get_instance()
                now_jst = datetime.datetime.now().astimezone(JST)

                usage_data = {
                    "date": now_jst,
                    "app_type": APP_TYPE,
                    "document_types": selected_document_type,
                    "model_detail": model_detail,
                    "department": selected_department,
                    "doctor": selected_doctor,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "processing_time": round(processing_time)
                }

                query = """
                        INSERT INTO summary_usage
                        (date, app_type, document_types, model_detail, department, doctor, input_tokens, output_tokens, \
                         total_tokens, processing_time)
                        VALUES (:date, :app_type, :document_types, :model_detail, :department, :doctor, :input_tokens, \
                                :output_tokens, :total_tokens, :processing_time) \
                        """

                db_manager.execute_query(query, usage_data, fetch=False)

            except Exception as db_error:
                st.warning(f"利用状況のDB保存中にエラーが発生しました: {str(db_error)}")

        else:
            raise result['error']

    except Exception as e:
        raise APIError(f"退院時サマリの作成中にエラーが発生しました: {str(e)}")
