# 変更履歴

プロジェクトのすべての注目すべき変更は、このファイルに記録されます。

このファイルのフォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

## [Unreleased]

## [1.2.0] - 2026-01-06

### 追加
- プロンプト管理機能のORM化：データベース操作をSQLAlchemyORM に統一し、保守性を向上
- 使用統計ページの機能向上：モデルマッピングを簡略化し、フィルタリングロジックを改善

### 変更
- `summary_service`と`navigation`：APP_TYPEをconfigからインポートするように修正
- `text_processor`：デフォルトセクション名で空文字列を返すように修正
- 退院時サマリの指示をより簡潔にするように改善
- `main_page`：入力テキストセッション状態の安全なクリア処理を実装

### 削除
- Gemini Flashモデルの提供を終了
- プロンプト管理における非推奨関数を削除：
  - `create_or_update_prompt`（ORM版に置き換え）
  - `delete_prompt`（ORM版に置き換え）
  - `initialize_default_prompt`（ORM版に置き換え）
  - `initialize_database`（ORM版に置き換え）
- `constants.py`の未使用APP_TYPEインポート削除
- `prompt_management.py`の未使用変数削除

### 修正
- `config.ini`のパスを`utils/config.ini`に修正
- セッション状態の安全なクリア処理：`additional_info`を空文字列にリセット
- Google認証情報の環境変数名を統一：`GEMINI_CREDENTIALS`から`GOOGLE_CREDENTIALS_JSON`に変更

### セキュリティ

## [1.1.0] - 2025-12-04

### 追加
- 複数AI API対応：Claude（Anthropic/Bedrock）とGeminiの統合
- プロンプト管理システム：部署・医師別のカスタマイズ機能
- PostgreSQLデータベース統合：プロンプト、使用統計、設定の永続化
- 使用統計ページ：AI API利用履歴と統計情報の表示
- 自動モデル切り替え機能：入力トークン数に基づいてモデルを自動選択
- 「前回の記載」機能：主治医意見書作成時の治療内容参照機能
- テキスト処理機能：医療文書の自動セクション分割
- セッション状態管理：ユーザー選択の保存と復元

### 変更
- テキストエリアの高さを70に調整
- Google認証情報の環境変数名を`GOOGLE_CREDENTIALS_JSON`に統一
- database操作をORMベースに統一

### 削除
- 不要な依存関係の削除：`pywin32`
