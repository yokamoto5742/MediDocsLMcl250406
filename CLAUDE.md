# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返すこと。Return patch diffs, not prose.
- 不明な点がある場合は、トレードオフを明記した2つの選択肢を提案すること（80語以内）。
- 変更範囲は最小限に抑えること
- Pythonコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

## Automatic Notifications (Hooks)
自動通知は`.claude/settings.local.json` で設定済：

- **Stop Hook**: ユーザーがClaude Codeを停止した時に「作業が完了しました」と通知
- **SessionEnd Hook**: セッション終了時に「Claude Code セッションが終了しました」と通知

## Key Commands

### Application Startup
```bash
streamlit run app.py
```

### Database Management
```bash
# Database migration (optional)
alembic upgrade head

# Database reset (development)
python scripts/db_reset.py

# Database initialization
python scripts/init_db.py
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_summary_service.py

# Run tests with coverage
python -m pytest --cov=.
```

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

This is a **Streamlit-based medical document generation application** that leverages multiple AI APIs (Claude, Gemini) to create medical documents from clinical notes.

### Core Architecture
- **Multi-page Streamlit app** with navigation state management
- **Factory pattern** for AI API clients supporting Claude (Anthropic/Bedrock) and Gemini (Google AI)
- **PostgreSQL database** with SQLAlchemy ORM for prompts, usage statistics, and settings
- **Modular prompt management** system with department/doctor-specific customization

### Data Flow
1. **Input Processing**: Clinical text → Token validation → Model selection
2. **AI Generation**: API Factory → Provider-specific client → Generated medical document
3. **Output Processing**: Response parsing → Section extraction → Database logging
4. **UI Rendering**: Tabbed display (全文/治療経過/特記事項/備考)

### Key Integration Points
- **`services/summary_service.py`**: Main business logic orchestrating the generation workflow
- **`external_service/api_factory.py`**: Central dispatcher for AI provider selection
- **`utils/prompt_manager.py`**: Dynamic prompt retrieval based on context (department/doctor/document type)
- **`database/models.py`**: Three main entities: Prompts, SummaryUsage, AppSettings

### Configuration Management
- **Environment variables** (`.env`) for API keys, database URLs, token limits
- **Department/doctor mappings** in `utils/constants.py`
- **Model switching logic** based on input token count thresholds

### State Management
- **Streamlit session state** for user selections, generated content, and navigation
- **Database persistence** for user preferences and usage tracking
- **Settings auto-save** functionality in navigation component

## Development Notes

### Adding New AI Providers
1. Create new client class inheriting from `BaseAPIClient` in `external_service/`
2. Add provider enum to `APIFactory` in `api_factory.py`
3. Update provider mapping and credential validation

### Database Schema Changes
- Use Alembic migrations for schema changes
- Models defined in `database/models.py` using SQLAlchemy declarative base
- Test database operations in isolation using pytest fixtures

### Prompt Customization
- Prompts are stored per (department, document_type, doctor) combination
- Fallback hierarchy: specific → department default → system default
- Prompt management UI available in the application

### Testing Strategy
- Comprehensive test coverage in `tests/` directory
- Mock external API calls using unittest.mock
- Database operations tested with temporary fixtures
- Streamlit components tested with suppressed logging