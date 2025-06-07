MESSAGES = {
    "PROMPT_UPDATED": "プロンプトを更新しました",
    "PROMPT_CREATED": "プロンプトを新規作成しました",
    "PROMPT_DELETED": "プロンプトを削除しました",

    "FIELD_REQUIRED": "すべての項目を入力してください",
    "NO_INPUT": "⚠️ カルテ情報を入力してください",
    "INPUT_TOO_SHORT": "⚠️ 入力テキストが短すぎます",
    "INPUT_TOO_LONG": "⚠️ 入力テキストが長すぎます",
    "TOKEN_THRESHOLD_EXCEEDED": "⚠️ 入力テキストが長いため{original_model} から Gemini_Pro に切り替えます",
    "TOKEN_THRESHOLD_EXCEEDED_NO_GEMINI": "⚠️ 入力テキストが長すぎます。Gemini APIの認証情報が設定されていないため処理できません。",
    "API_CREDENTIALS_MISSING": "⚠️ Gemini APIの認証情報が設定されていません。環境変数を確認してください。",
    "CLAUDE_API_CREDENTIALS_MISSING": "⚠️ Claude APIの認証情報が設定されていません。環境変数を確認してください。",
    "OPENAI_API_CREDENTIALS_MISSING": "⚠️ OpenAI APIの認証情報が設定されていません。環境変数を確認してください。",
    "OPENAI_API_QUOTA_EXCEEDED": "⚠️ OpenAI APIのクォータを超過しています。請求情報を確認するか、管理者に連絡してください。",
    "NO_API_CREDENTIALS": "⚠️ 使用可能なAI APIの認証情報が設定されていません。環境変数を確認してください。",
}

TAB_NAMES = {
    "ALL": "全文",
    "TREATMENT": "治療経過",
    "SPECIAL": "特記事項",
    "NOTE": "備考"
}

DEFAULT_SECTION_NAMES = ["治療経過", "特記事項", "備考"]

APP_TYPE = "opinion_letter"
DEFAULT_DEPARTMENT = ["default"]
DEFAULT_DOCTOR = ["default"]
DEFAULT_DOCUMENT_TYPE = "主治医意見書"
DOCUMENT_TYPES = ["主治医意見書", "訪問看護指示書"]
DOCUMENT_TYPE_OPTIONS = ["すべて", "主治医意見書", "訪問看護指示書"]

DEPARTMENT_DOCTORS_MAPPING = {
    "default": ["default"],
}
