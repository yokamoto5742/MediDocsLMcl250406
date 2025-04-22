import datetime
import pandas as pd
import streamlit as st
from utils.error_handlers import handle_error
from utils.db import get_usage_collection
from ui_components.navigation import change_page

MODEL_MAPPING = {
    "Gemini_Pro": {"pattern": "gemini", "exclude": "flash"},
    "Gemini_Flash": {"pattern": "flash", "exclude": None},
    "Claude": {"pattern": "claude", "exclude": None}
}


@handle_error
def usage_statistics_ui():
    if st.button("作成画面に戻る", key="back_to_main_from_stats"):
        change_page("main")
        st.rerun()

    usage_collection = get_usage_collection()

    col1, col2 = st.columns(2)

    with col1:
        today = datetime.datetime.now().date()
        start_date = st.date_input("開始日", today - datetime.timedelta(days=7))

    with col2:
        models = ["すべて", "Claude", "Gemini_Pro", "Gemini_Flash"]
        selected_model = st.selectbox("AIモデル", models, index=0)

    col3, col4 = st.columns(2)

    with col3:
        end_date = st.date_input("終了日", today)

    with col4:
        app_types = ["退院時サマリ", "不明", "すべて"]
        selected_app_type = st.selectbox("文書名", app_types, index=0)

    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

    query = {
        "date": {
            "$gte": start_datetime,
            "$lte": end_datetime
        }
    }

    if selected_model != "すべて":
        model_config = MODEL_MAPPING.get(selected_model)
        if model_config:
            query["model_detail"] = {"$regex": model_config["pattern"], "$options": "i"}
            if model_config["exclude"]:
                query["model_detail"]["$not"] = {"$regex": model_config["exclude"], "$options": "i"}

    if selected_app_type != "すべて":
        if selected_app_type == "不明":
            query["app_type"] = {"$exists": False}
        else:
            query["app_type"] = selected_app_type

    total_summary = usage_collection.aggregate([
        {"$match": query},
        {"$group": {
            "_id": None,
            "count": {"$sum": 1},
            "total_input_tokens": {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"},
            "total_tokens": {"$sum": "$total_tokens"}
        }}
    ])

    total_summary = list(total_summary)

    if not total_summary:
        st.info("指定した期間のデータがありません")
        return

    dept_summary = usage_collection.aggregate([
        {"$match": query},
        {"$group": {
            "_id": {"department": "$department", "app_type": "$app_type"},
            "count": {"$sum": 1},
            "input_tokens": {"$sum": "$input_tokens"},
            "output_tokens": {"$sum": "$output_tokens"},
            "total_tokens": {"$sum": "$total_tokens"}
        }},
        {"$sort": {"count": -1}}
    ])

    dept_summary = list(dept_summary)

    records = usage_collection.find(
        query,
        {
            "date": 1,
            "model_detail": 1,
            "input_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 1,
            "_id": 0
        }
    ).sort("date", -1)

    data = []
    for stat in dept_summary:
        dept_name = "全科共通" if stat["_id"]["department"] == "default" else stat["_id"]["department"]
        app_type = stat["_id"].get("app_type", "不明")
        data.append({
            "診療科": dept_name,
            "文書名": app_type,
            "作成件数": stat["count"],
            "入力トークン": stat["input_tokens"],
            "出力トークン": stat["output_tokens"],
            "合計トークン": stat["total_tokens"]
        })

    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True)

    detail_data = []
    for record in records:
        model_detail = str(record.get("model_detail", "")).lower()
        model_info = "Claude"  # デフォルト値

        for model_name, config in MODEL_MAPPING.items():
            pattern = config["pattern"]
            exclude = config["exclude"]

            if pattern in model_detail:
                if exclude and exclude in model_detail:
                    continue
                model_info = model_name
                break

        detail_data.append({
            "作成日": record["date"].strftime("%Y-%m-%d"),
            "AIモデル": model_info,
            "入力トークン": record["input_tokens"],
            "出力トークン": record["output_tokens"],
            "合計トークン": record["total_tokens"]
        })

    detail_df = pd.DataFrame(detail_data)
    st.dataframe(detail_df, hide_index=True)
