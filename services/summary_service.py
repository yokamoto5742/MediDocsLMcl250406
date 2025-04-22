import datetime
import threading
import time
import queue  # スレッド間通信用

import streamlit as st

from external_service.claude_api import claude_generate_discharge_summary
from external_service.gemini_api import gemini_generate_discharge_summary
from utils.constants import APP_TYPE, DOCUMENT_NAME, MESSAGES
from utils.error_handlers import handle_error
from utils.exceptions import APIError
from utils.text_processor import format_discharge_summary, parse_discharge_summary
from utils.db import get_usage_collection
from utils.config import GEMINI_CREDENTIALS, CLAUDE_API_KEY, GEMINI_MODEL, GEMINI_FLASH_MODEL, MAX_INPUT_TOKENS, MIN_INPUT_TOKENS


@handle_error
def process_discharge_summary(input_text):
    """
    入力テキストを受け取り、選択されたモデルを使用して退院時サマリを生成し、
    結果をセッションステートとデータベースに保存する。
    処理中は経過時間をカウントアップ表示する。
    """
    # --- APIキー/認証情報のチェック ---
    if not GEMINI_CREDENTIALS and not CLAUDE_API_KEY:
        raise APIError(MESSAGES["NO_API_CREDENTIALS"])

    # --- 入力テキストのチェック ---
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

    # --- 処理開始 ---
    try:
        start_time = datetime.datetime.now()
        status_placeholder = st.empty()  # 経過時間表示用のプレースホルダー
        result_queue = queue.Queue()  # スレッド間通信用のキュー

        # セッションステートから選択されたモデルを取得
        available_models = getattr(st.session_state, "available_models", [])
        selected_model = getattr(st.session_state, "selected_model",
                                 available_models[0] if available_models else None)

        # 選択された部署を取得
        selected_department = getattr(st.session_state, "selected_department", "default")

        # --- サマリ生成タスク (別スレッドで実行) ---
        def generate_summary_task(input_text, selected_department, selected_model, result_queue):
            """サマリ生成処理（API呼び出し、フォーマット、パース）を実行する関数"""
            try:
                # モデル選択とAPI呼び出し
                if selected_model == "Claude" and CLAUDE_API_KEY:
                    discharge_summary, input_tokens, output_tokens = claude_generate_discharge_summary(
                        input_text,
                        selected_department,
                    )
                    model_detail = selected_model
                elif selected_model == "Gemini_Pro" and GEMINI_MODEL and GEMINI_CREDENTIALS:
                    discharge_summary, input_tokens, output_tokens = gemini_generate_discharge_summary(
                        input_text,
                        selected_department,
                        GEMINI_MODEL,
                    )
                    model_detail = GEMINI_MODEL
                elif selected_model == "Gemini_Flash" and GEMINI_FLASH_MODEL and GEMINI_CREDENTIALS:
                    discharge_summary, input_tokens, output_tokens = gemini_generate_discharge_summary(
                        input_text,
                        selected_department,
                        GEMINI_FLASH_MODEL,
                    )
                    model_detail = GEMINI_FLASH_MODEL
                else:
                    # 利用可能なモデルがない、または選択されたモデルに対応するキーがない場合
                    raise APIError(MESSAGES["NO_API_CREDENTIALS"])

                # 結果のフォーマットとパース
                discharge_summary = format_discharge_summary(discharge_summary)
                parsed_summary = parse_discharge_summary(discharge_summary)

                # 成功結果をキューに入れる
                result_queue.put({
                    "success": True,
                    "discharge_summary": discharge_summary,
                    "parsed_summary": parsed_summary,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model_detail": model_detail
                })

            except Exception as e:
                # エラーをキューに入れる
                result_queue.put({"success": False, "error": e})

        # --- スレッドの開始とカウントアップ表示 ---
        summary_thread = threading.Thread(
            target=generate_summary_task,
            args=(input_text, selected_department, selected_model, result_queue)
        )
        summary_thread.start()

        elapsed_time = 0
        # スレッドが終了するまで1秒ごとに表示を更新
        with st.spinner("退院時サマリを作成中..."):
            while summary_thread.is_alive():
                status_placeholder.text(f"⏱️ 経過時間: {elapsed_time}秒")
                time.sleep(1)
                # datetimeを使って正確な経過時間を計算
                elapsed_time = int((datetime.datetime.now() - start_time).total_seconds())

        # スレッド終了待ち
        summary_thread.join()

        # プレースホルダー（カウントアップ表示）をクリア
        status_placeholder.empty()

        # --- 結果の取得と処理 ---
        result = result_queue.get()

        if result["success"]:
            # --- 成功時の処理 ---
            # セッションステートに結果を保存
            st.session_state.discharge_summary = result["discharge_summary"]
            st.session_state.parsed_summary = result["parsed_summary"]

            # 処理時間とトークン数を取得
            input_tokens = result["input_tokens"]
            output_tokens = result["output_tokens"]
            model_detail = result["model_detail"]
            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            st.session_state.summary_generation_time = processing_time

            # --- DBへの利用状況保存 ---
            try:
                usage_collection = get_usage_collection()
                usage_data = {
                    "date": datetime.datetime.now(),
                    "app_type": APP_TYPE,
                    "document_name": DOCUMENT_NAME,
                    "model_detail": model_detail,
                    "department": selected_department,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "processing_time": processing_time
                }
                usage_collection.insert_one(usage_data)
            except Exception as db_error:
                # DB保存エラーは警告に留め、メイン処理の成功は妨げない
                st.warning(f"利用状況のDB保存中にエラーが発生しました: {str(db_error)}")

        else:
            # --- エラー発生時の処理 ---
            # スレッド内で発生したエラーを再度raise
            raise result['error']

    except Exception as e:
        # --- 全体的なエラーハンドリング ---
        raise APIError(f"退院時サマリの作成中にエラーが発生しました: {str(e)}")