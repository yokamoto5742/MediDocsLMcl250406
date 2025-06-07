import pytest
from unittest.mock import Mock, patch
from external_service.api_factory import APIFactory, APIProvider
from external_service.claude_api import ClaudeAPIClient
from external_service.openai_api import OpenAIAPIClient
from external_service.gemini_api import GeminiAPIClient
from utils.exceptions import APIError


class TestAPIFactory:
    """APIFactoryクラスのテスト"""

    def test_create_client_with_enum_claude(self):
        """APIProvider.CLAUDEでClaudeAPIClientを作成するテスト"""
        with patch('external_service.api_factory.ClaudeAPIClient') as mock_claude:
            mock_client = Mock()
            mock_claude.return_value = mock_client
            
            result = APIFactory.create_client(APIProvider.CLAUDE)
            
            mock_claude.assert_called_once()
            assert result == mock_client

    def test_create_client_with_enum_openai(self):
        """APIProvider.OPENAIでOpenAIAPIClientを作成するテスト"""
        with patch('external_service.api_factory.OpenAIAPIClient') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            result = APIFactory.create_client(APIProvider.OPENAI)
            
            mock_openai.assert_called_once()
            assert result == mock_client

    def test_create_client_with_enum_gemini(self):
        """APIProvider.GEMINIでGeminiAPIClientを作成するテスト"""
        with patch('external_service.api_factory.GeminiAPIClient') as mock_gemini:
            mock_client = Mock()
            mock_gemini.return_value = mock_client
            
            result = APIFactory.create_client(APIProvider.GEMINI)
            
            mock_gemini.assert_called_once()
            assert result == mock_client

    def test_create_client_with_string_claude(self):
        """文字列"claude"でClaudeAPIClientを作成するテスト"""
        with patch('external_service.api_factory.ClaudeAPIClient') as mock_claude:
            mock_client = Mock()
            mock_claude.return_value = mock_client
            
            result = APIFactory.create_client("claude")
            
            mock_claude.assert_called_once()
            assert result == mock_client

    def test_create_client_with_string_case_insensitive(self):
        """大文字小文字を無視して正しく動作するテスト"""
        with patch('external_service.api_factory.OpenAIAPIClient') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            result = APIFactory.create_client("OPENAI")
            
            mock_openai.assert_called_once()
            assert result == mock_client

    def test_create_client_with_invalid_string(self):
        """無効な文字列でAPIErrorが発生するテスト"""
        with pytest.raises(APIError, match="未対応のAPIプロバイダー"):
            APIFactory.create_client("invalid_provider")

    def test_create_client_with_invalid_enum(self):
        """無効なEnumでAPIErrorが発生するテスト（理論上は発生しないが）"""
        with pytest.raises(APIError, match="未対応のAPIプロバイダー"):
            # 直接無効なenumは作れないので、mockで無効なproviderを作成
            invalid_provider = Mock()
            invalid_provider.value = "invalid"
            APIFactory.create_client(invalid_provider)

    @patch('external_service.api_factory.APIFactory.create_client')
    def test_generate_summary_with_provider(self, mock_create_client):
        """generate_summary_with_providerメソッドのテスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"
        sample_additional_info = "追加情報のテストデータ"

        # モッククライアントのセットアップ
        mock_client = Mock()
        mock_client.generate_summary.return_value = ("サマリーテキスト", 100, 50)
        mock_create_client.return_value = mock_client

        # テスト実行
        result = APIFactory.generate_summary_with_provider(
            provider=APIProvider.CLAUDE,
            medical_text=sample_medical_text,
            additional_info=sample_additional_info,
            department="内科",
            document_type="診断書",
            doctor="田中医師",
            model_name="claude-3-sonnet"
        )

        # 検証
        mock_create_client.assert_called_once_with(APIProvider.CLAUDE)
        mock_client.generate_summary.assert_called_once_with(
            sample_medical_text,
            sample_additional_info,
            "内科",
            "診断書",
            "田中医師",
            "claude-3-sonnet"
        )
        assert result == ("サマリーテキスト", 100, 50)

    @patch('external_service.api_factory.APIFactory.generate_summary_with_provider')
    def test_generate_summary_function(self, mock_generate_summary_with_provider):
        """グローバルgenerate_summary関数のテスト"""
        from external_service.api_factory import generate_summary

        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        mock_generate_summary_with_provider.return_value = ("テストサマリー", 80, 40)

        result = generate_summary(
            provider="openai",
            medical_text=sample_medical_text,
            department="外科",
            model_name="gpt-4"
        )

        mock_generate_summary_with_provider.assert_called_once_with(
            "openai",
            sample_medical_text,
            department="外科",
            model_name="gpt-4"
        )
        assert result == ("テストサマリー", 80, 40)
