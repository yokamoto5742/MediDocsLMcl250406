MESSAGES = {
    "PROMPT_UPDATED": "プロンプトを更新しました",
    "PROMPT_CREATED": "プロンプトを新規作成しました",
    "PROMPT_DELETED": "プロンプトを削除しました",

    "DEPARTMENT_EXISTS": "この診療科は既に存在します",
    "DEPARTMENT_CREATED": "診療科を登録しました",
    "DEPARTMENT_DELETED": "診療科を削除しました",

    "FIELD_REQUIRED": "すべての項目を入力してください",
    "NO_INPUT": "⚠️ カルテ情報を入力してください",
    "INPUT_TOO_SHORT": "⚠️ 入力テキストが短すぎます",
    "INPUT_TOO_LONG": "⚠️ 入力テキストが長すぎます",
    "API_CREDENTIALS_MISSING": "⚠️ Gemini APIの認証情報が設定されていません。環境変数を確認してください。",
    "CLAUDE_API_CREDENTIALS_MISSING": "⚠️ Claude APIの認証情報が設定されていません。環境変数を確認してください。",
    "OPENAI_API_CREDENTIALS_MISSING": "⚠️ OpenAI APIの認証情報が設定されていません。環境変数を確認してください。",
    "NO_API_CREDENTIALS": "⚠️ 使用可能なAI APIの認証情報が設定されていません。環境変数を確認してください。",
}

DEFAULT_DEPARTMENTS = ["内科", "消化器内科", "整形外科", "眼科"]
DEFAULT_SECTION_NAMES = ["入院期間", "現病歴", "入院時検査", "入院中の治療経過", "退院申し送り", "備考"]

APP_TYPE = "discharge_summary"
DEFAULT_DOCUMENT_NAME = "退院時サマリ"
DEFAULT_DOCUMENT_TYPES = ["退院時サマリ", "現病歴", "主治医意見書", "訪問看護指示書"]
DOCUMENT_NAME_OPTIONS = ["すべて", "不明"]

DEFAULT_DOCTORS = ["default", "田中医師", "佐々木医師", "鈴木医師", "高田医師", "山田医師"]

DEPARTMENT_DOCTORS_MAPPING = {
    "default": ["default"],  # 全科共通には default のみを関連付け
    "内科": ["default", "田中医師", "佐々木医師"],
    "消化器内科": ["default", "山田医師"],
    "整形外科": ["default", "鈴木医師", "高田医師"],
    "眼科": ["default", "高田医師"]
}
