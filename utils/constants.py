from utils.config import APP_TYPE

MESSAGES = {
    "PROMPT_UPDATED": "プロンプトを更新しました",
    "PROMPT_CREATED": "プロンプトを新規作成しました",
    "PROMPT_DELETED": "プロンプトを削除しました",

    "NO_DATA_FOUND": "指定期間のデータがありません",

    "FIELD_REQUIRED": "すべての項目を入力してください",
    "NO_INPUT": "⚠️ カルテ情報を入力してください",
    "INPUT_TOO_SHORT": "⚠️ 入力テキストが短すぎます",
    "INPUT_TOO_LONG": "⚠️ 入力テキストが長すぎます",
    "TOKEN_THRESHOLD_EXCEEDED": "⚠️ 入力テキストが長いため{original_model} から Gemini_Pro に切り替えます",
    "TOKEN_THRESHOLD_EXCEEDED_NO_GEMINI": "⚠️ Gemini APIの認証情報が設定されていないため処理できません。",

    "API_CREDENTIALS_MISSING": "⚠️ Gemini APIの認証情報が設定されていません。環境変数を確認してください。",
    "NO_API_CREDENTIALS": "⚠️ 使用可能なAI APIの認証情報が設定されていません。環境変数を確認してください。",

    "AWS_CREDENTIALS_MISSING": "⚠️ AWS認証情報が設定されていません。環境変数を確認してください。",
    "ANTHROPIC_MODEL_MISSING": "⚠️ ANTHROPIC_MODELが設定されていません。環境変数を確認してください。",
    "BEDROCK_INIT_ERROR": "Amazon Bedrock Claude API初期化エラー: {error}",
    "BEDROCK_API_ERROR": "Amazon Bedrock Claude API呼び出しエラー: {error}",

    "EMPTY_RESPONSE": "レスポンスが空です",

    "COPY_INSTRUCTION": "💡 テキストエリアの右上にマウスを合わせて左クリックでコピーできます",
    "PROCESSING_TIME": "⏱️ 処理時間: {processing_time:.0f}秒",
}

TAB_NAMES = {
    "ALL": "全文",
    "TREATMENT": "治療経過",
    "SPECIAL": "特記事項",
    "NOTE": "備考"
}

DEFAULT_SECTION_NAMES = ["治療経過", "特記事項", "備考"]

DEFAULT_DEPARTMENT = ["default"]
DEFAULT_DOCTOR = ["default"]
DEFAULT_DOCUMENT_TYPE = "主治医意見書"
DOCUMENT_TYPES = ["主治医意見書", "訪問看護指示書"]
DOCUMENT_TYPE_OPTIONS = ["すべて", "主治医意見書", "訪問看護指示書"]

DEPARTMENT_DOCTORS_MAPPING = {
    "default": ["default"],
}
