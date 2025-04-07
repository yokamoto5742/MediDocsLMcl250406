class AppError(Exception):
    """アプリケーションの基本例外クラス"""
    pass

class AuthError(AppError):
    """認証関連のエラー"""
    pass

class APIError(AppError):
    """外部API（Gemini等）関連のエラー"""
    pass

class DatabaseError(AppError):
    """データベース操作関連のエラー"""
    pass