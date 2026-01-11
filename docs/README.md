# 主治医意見書作成アプリ

このアプリケーションは、生成AIを活用して主治医意見書、訪問看護指示書を効率的に作成するためのWebアプリケーションです。

## 主な機能

### 📋 文書作成機能
- **主治医意見書**と**訪問看護指示書**の文書の自動生成
- 前回の記載、カルテ情報、追加情報を入力するだけで高精度な文書を作成
- 生成結果は「全文」「治療経過」「特記事項」「備考」のタブ形式で表示
- 改行と折り返しが適切に表示されるコードブロック対応

### 🔍 文書評価機能
- 生成された医療文書を自動評価
- 評価進捗表示と処理時間の表示機能
- 評価完了時のメッセージ通知機能

### 🤖 複数AIモデル対応
- **Claude** (Anthropic)
- **Gemini** (Google)
- 入力文字数に応じた自動モデル切り替え機能

### ⚙️ カスタマイズ機能
- 文書タイプごとの専用プロンプト設定
- AIモデルの選択・設定保存

### 📊 統計・管理機能
- 使用状況の統計表示（作成件数、トークン使用量、処理時間）
- 期間・モデル・文書タイプでの絞り込み表示
- PostgreSQLによるデータ永続化

## システム要件

### 必要なソフトウェア
- Python 3.11以上
- PostgreSQL 16以上

### 必要なAPIキー・認証情報
以下のいずれか1つ以上のAPIキーが必要です：
- **Claude API**: AWS Bedrock経由でのAnthropic Claude APIアクセス
- **Gemini API**: Google Cloud Vertex AI経由でのGemini APIアクセス（サービスアカウントJSON認証）

## インストール手順

### 1. リポジトリのクローン
```bash
git clone <リポジトリURL>
cd medical-document-generator
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`.env`ファイルを作成し、以下の設定を行ってください：

```env
# データベース設定（PostgreSQL）
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# AI API設定（いずれか1つ以上設定）
# Claude API (AWS Bedrock)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Gemini API (Google Cloud Vertex AI Service Account JSON)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project"...}
GOOGLE_PROJECT_ID=your-google-cloud-project-id
GOOGLE_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-thinking-exp
GEMINI_THINKING_BUDGET=10000

# トークン制限設定
MAX_INPUT_TOKENS=200000
MIN_INPUT_TOKENS=100
MAX_TOKEN_THRESHOLD=40000
```

### 5. データベースの初期化
```bash
# Alembicマイグレーション（オプション）
alembic upgrade head

# または自動初期化（アプリ起動時に実行）
```

## 使用方法

### アプリケーションの起動
```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス

### 基本的な使い方

#### 1. 文書作成
1. **サイドバー**で診療科、医師名、文書タイプ、AIモデルを選択
2. **前回の記載**に前回作成した主治医意見書の治療内容を入力（任意）
3. **カルテ記載**にカルテ情報を入力
4. **追加情報**に補足情報や特記事項を入力（任意）
5. **「作成」ボタン**をクリック
6. 生成された文書をコピーして確認

#### 2. プロンプト管理
1. サイドバーの**「プロンプト管理」**をクリック
2. 診療科、医師名、文書タイプを選択
3. プロンプト内容を編集
4. **「保存」**をクリック

#### 3. 文書評価設定
1. サイドバーの**「評価設定」**をクリック
2. 文書タイプごとの評価プロンプントを設定
3. 評価ルールをカスタマイズ

#### 4. 統計情報確認
1. サイドバーの**「統計情報」**をクリック
2. 期間、モデル、文書タイプで絞り込み
3. 使用状況と詳細レコードを確認

## 設定カスタマイズ

### 診療科・医師の追加
`utils/constants.py`の以下の部分を編集：

```python
DEFAULT_DEPARTMENT = ["default", "内科", "外科", "整形外科"]

DEPARTMENT_DOCTORS_MAPPING = {
    "default": ["default"],
    "内科": ["default", "田中医師", "佐藤医師"],
    "外科": ["default", "山田医師"],
}
```

## 開発者向け情報

### プロジェクト構造
```
├── app.py                    # メインアプリケーション
├── config.ini               # 設定ファイル
├── database/                # データベース関連
│   ├── db.py                # DB接続・操作
│   ├── models.py            # SQLAlchemyモデル
│   └── schema.py            # テーブル作成・マイグレーション
├── external_service/        # 外部API連携
│   ├── api_factory.py       # APIファクトリー
│   ├── base_api.py          # 基底APIクラス
│   ├── claude_api.py        # Claude API
│   ├── gemini_api.py        # Gemini API
│   └── gemini_evaluation.py # 文書評価用API
├── services/                # ビジネスロジック
│   ├── summary_service.py   # サマリー生成サービス
│   └── evaluation_service.py# 文書評価サービス
├── ui_components/           # UIコンポーネント
│   └── navigation.py        # ナビゲーション・設定
├── utils/                   # ユーティリティ
│   ├── config.ini           # 設定管理
│   ├── config.py            # 設定管理
│   ├── constants.py         # 定数定義
│   ├── exceptions.py        # 例外クラス
│   ├── prompt_manager.py    # プロンプト管理
│   └── text_processor.py    # テキスト処理
└── views/                   # ページビュー
    ├── main_page.py         # メインページ
    ├── prompt_management_page.py  # プロンプト管理
    ├── evaluation_settings_page.py# 評価設定ページ
    └── statistics_page.py   # 統計ページ
```

### データベーステーブル
- **prompts**: プロンプト管理
- **summary_usage**: 使用統計
- **evaluation_prompts**: 文書評価プロンプト
- **app_settings**: アプリケーション設定

### APIクライアント追加
新しいAIプロバイダーを追加する場合：

1. `external_service/`に新しいAPIクライアントを作成
2. `BaseAPIClient`を継承
3. `api_factory.py`にプロバイダーを追加

### 文書評価機能
文書評価機能は以下のコンポーネントで構成されています：
- **evaluation_service.py**: 評価プロンプトの管理と評価実行
- **gemini_evaluation.py**: Gemini APIによる文書評価
- **evaluation_settings_page.py**: 評価プロンプト設定UI
- **evaluation_prompts テーブル**: 文書タイプごとの評価ルール保存

評価は非同期で実行され、進捗表示と処理時間を表示します。

## トラブルシューティング

### よくある問題

#### データベース接続エラー
- PostgreSQLサービスが起動しているか確認
- 環境変数の設定を再確認
- データベースとユーザーの権限を確認

#### API認証エラー
- Claude API: AWS認証情報（Access Key ID、Secret Access Key、Region）が正しく設定されているか確認
- Gemini API: Google Cloud認証情報（GOOGLE_CREDENTIALS_JSON、PROJECT_ID、LOCATION）が正しく設定されているか確認
- APIキーの有効期限と使用制限を確認
- ネットワーク接続を確認

#### トークン数超過エラー
- 入力テキストの長さを調整
- `MAX_TOKEN_THRESHOLD`の値を調整
- Gemini APIを有効にして自動切り替えを利用

#### 文書評価エラー
- 評価設定ページで評価プロンプントが正しく設定されているか確認
- Gemini APIの認証情報が正しく設定されているか確認
- 文書タイプが評価プロンプントデータベースに登録されているか確認

### ログ確認
アプリケーションのログはコンソールに出力されます。エラーの詳細は実行時のログを確認してください。

### ライセンス

このプロジェクトは[Apache License 2.0](LICENSE)のもとで公開されています。

### 免責事項
このアプリケーションは医療文書作成の支援ツールです。生成された文書は必ず医療従事者による確認・承認を経てご使用ください。本ソフトウェアの使用により生じたいかなる損害についても、開発者は責任を負いません。
