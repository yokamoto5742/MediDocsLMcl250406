# Changelog

All notable changes to the Medical Document Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ✨ **Previous Record Input**: Added "前回の記載" input field to capture previous medical document content
- 🔧 **Enhanced Prompt Integration**: Previous record content is now included in AI prompts for better context
- 📝 **UI Improvements**: Optimized text area heights (70px) for better user experience
- 🛠️ Claude Code configuration and hooks setup

### Changed
- 🔄 **Credential Management**: Completely migrated from GEMINI_CREDENTIALS to GOOGLE_CREDENTIALS_JSON
- 📖 **Documentation Update**: Updated README.md to reflect new input fields and authentication methods
- 🎯 **Data Flow Enhancement**: Updated entire service chain to pass previous record through all functions
- 📋 **Prompt Template**: Modified prompt structure to include: 【前回の記載】→【カルテ情報】→【追加情報】

### Technical Improvements
- 🏗️ **Service Layer**: Updated process_summary(), execute_summary_generation_with_ui(), generate_summary_task()
- 🔌 **API Layer**: Enhanced base_api.py and api_factory.py to support previous record parameter
- 🧪 **Test Updates**: Updated all test files to use GOOGLE_CREDENTIALS_JSON instead of GEMINI_CREDENTIALS
- 📚 **Documentation**: Comprehensive README updates covering new features and correct authentication setup

## [2025-09-16] - Test Suite Modernization

### Fixed
- 🧪 **Test Suite Overhaul**: Fixed all failing tests after OpenAI provider removal
  - Removed deprecated OpenAI-related test cases from test_summary_service.py
  - Updated test_config.py to match current AWS/Anthropic configuration
  - Fixed character encoding issues in error messages
  - Corrected API credential validation tests for current architecture
- ✅ **Full Test Coverage**: All 120 tests now pass successfully
- 🔧 **Configuration Tests**: Updated environment variable tests to reflect AWS Bedrock setup
- 🌐 **Error Message Localization**: Fixed character encoding issues in exception messages

### Changed
- 🎯 **Test Architecture**: Streamlined test structure to match current AI provider setup
- 📝 **Test Documentation**: Improved test clarity and reduced maintenance overhead
- 🏗️ **Assertion Logic**: Updated test assertions to match boolean credential handling

### Removed
- ❌ **OpenAI Legacy**: Completely removed OpenAI-related test code and references

## [2025-09-15] - Latest Updates

### Added
- ✨ **Vertex AI Integration**: Enhanced Gemini API with proper Vertex AI support
- 🔧 **Type Safety**: Added comprehensive type hints to external service modules
- 📦 **Dependencies Update**: Organized and updated requirements.txt with new AI service dependencies
- ⚙️ **Environment Variables**: New environment variable handling for Google Cloud services

### Changed
- 🔄 **Gemini API Refactor**: Complete rewrite of Gemini API client for Vertex AI compatibility
- 🛡️ **Error Handling**: Improved exception handling and error messages for AI API calls
- 🎯 **Model Selection**: Enhanced model switching logic based on input token thresholds

### Fixed
- 🐛 **API Initialization**: Fixed Vertex AI initialization and credential handling
- 🔧 **Content Generation**: Improved generate_content method with proper exception handling
- 📊 **Token Counting**: Fixed token usage tracking for both Claude and Gemini APIs

## [2025-09-12] - Amazon Bedrock Integration

### Added
- 🚀 **Amazon Bedrock Support**: Integrated Claude API via Amazon Bedrock
- 🔐 **AWS Authentication**: Added AWS credentials handling for Bedrock access
- 🌐 **Environment Configuration**: Enhanced environment variable management

### Changed
- 🔄 **Claude API Migration**: Migrated from direct Anthropic API to Bedrock implementation
- 📱 **UI Updates**: Updated navigation components with improved user messaging
- ⚙️ **Configuration Management**: Enhanced config.py with AWS-specific settings

### Technical Improvements
- 🏗️ **Architecture**: Improved API factory pattern for multiple provider support
- 🛠️ **Error Handling**: Enhanced error messages and exception handling
- 📊 **Monitoring**: Better logging and debugging capabilities

## [Previous Versions]

### Core Features Implemented
- 📋 **Document Generation**: Medical document creation with AI assistance
- 🤖 **Multi-AI Support**: Claude and Gemini API integration
- 🗄️ **Database Management**: PostgreSQL with SQLAlchemy ORM
- 🎨 **Streamlit UI**: User-friendly web interface
- ⚙️ **Prompt Management**: Customizable prompts per department/doctor
- 📊 **Usage Statistics**: Comprehensive usage tracking and analytics
- 🔧 **Configuration System**: Flexible settings and preferences

### Database Schema
- **prompts**: Template management with hierarchical fallback
- **summary_usage**: Detailed usage statistics and performance metrics
- **app_settings**: User preferences and application configuration

### Testing Infrastructure
- 🧪 **Test Suite**: Comprehensive pytest-based testing
- 🎭 **Mocking**: External API mocking for reliable testing
- 🏗️ **Fixtures**: Database and configuration fixtures for isolated testing

---

## Development Notes

### Recent Focus Areas
1. **Test Infrastructure**: Complete modernization of test suite after architecture changes
2. **AI Provider Integration**: Stabilizing Claude (Bedrock) and Gemini (Vertex AI) connections
3. **Type Safety**: Improving code quality with comprehensive type hints
4. **Error Handling**: Robust exception handling across all API interactions
5. **Documentation**: Enhanced project documentation for better maintainability

### Next Priorities
- Performance optimization for large document processing
- Advanced prompt template features
- Enhanced usage analytics and reporting
- Mobile-responsive UI improvements

### Technical Achievements
- ✅ **100% Test Pass Rate**: All 120 tests successfully pass
- ✅ **Modern Architecture**: Clean separation of AI providers (Claude + Gemini only)
- ✅ **Robust Error Handling**: Comprehensive exception management
- ✅ **Type Safety**: Full type hint coverage for critical modules