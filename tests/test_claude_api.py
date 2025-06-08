from unittest.mock import Mock, patch

import pytest

from external_service.claude_api import ClaudeAPIClient
from utils.exceptions import APIError


class TestClaudeAPIClient:
    """ClaudeAPIClientクラスのテスト"""

    @patch('external_service.claude_api.CLAUDE_API_KEY', 'test_claude_key')
    @patch('external_service.claude_api.CLAUDE_MODEL', 'claude-3-sonnet')
    def test_init(self):
        """初期化テスト"""
        client = ClaudeAPIClient()
        assert client.api_key == 'test_claude_key'
        assert client.default_model == 'claude-3-sonnet'
        assert client.client is None

    @patch('external_service.claude_api.CLAUDE_API_KEY', 'valid_api_key')
    @patch('external_service.claude_api.Anthropic')
    def test_initialize_success(self, mock_anthropic):
        """正常な初期化テスト"""
        mock_anthropic_instance = Mock()
        mock_anthropic.return_value = mock_anthropic_instance
        
        client = ClaudeAPIClient()
        result = client.initialize()
        
        assert result is True
        assert client.client == mock_anthropic_instance
        mock_anthropic.assert_called_once_with(api_key='valid_api_key')

    @patch('external_service.claude_api.CLAUDE_API_KEY', '')
    def test_initialize_missing_api_key(self):
        """APIキー未設定時の初期化エラーテスト"""
        client = ClaudeAPIClient()
        
        with pytest.raises(APIError, match="Claude API初期化エラー"):
            client.initialize()

    @patch('external_service.claude_api.CLAUDE_API_KEY', 'valid_api_key')
    @patch('external_service.claude_api.Anthropic')
    def test_initialize_anthropic_error(self, mock_anthropic):
        """Anthropic初期化エラーテスト"""
        mock_anthropic.side_effect = Exception("接続エラー")
        
        client = ClaudeAPIClient()
        
        with pytest.raises(APIError, match="Claude API初期化エラー: 接続エラー"):
            client.initialize()

    def test_generate_content_success(self):
        """正常なコンテンツ生成テスト"""
        client = ClaudeAPIClient()
        
        # モックレスポンスの作成
        mock_content = Mock()
        mock_content.text = "生成されたサマリーテキスト"
        
        mock_usage = Mock()
        mock_usage.input_tokens = 150
        mock_usage.output_tokens = 75
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        mock_response.usage = mock_usage
        
        # モッククライアントの設定
        mock_anthropic_client = Mock()
        mock_anthropic_client.messages.create.return_value = mock_response
        client.client = mock_anthropic_client
        
        # テスト実行
        result = client._generate_content("テストプロンプト", "claude-3-sonnet")
        
        # 検証
        assert result == ("生成されたサマリーテキスト", 150, 75)
        mock_anthropic_client.messages.create.assert_called_once_with(
            model="claude-3-sonnet",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": "テストプロンプト"}
            ]
        )

    def test_generate_content_empty_response(self):
        """空のレスポンス処理テスト"""
        client = ClaudeAPIClient()
        
        # 空のコンテンツを持つモックレスポンス
        mock_usage = Mock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 0
        
        mock_response = Mock()
        mock_response.content = []  # 空のコンテンツ
        mock_response.usage = mock_usage
        
        mock_anthropic_client = Mock()
        mock_anthropic_client.messages.create.return_value = mock_response
        client.client = mock_anthropic_client
        
        result = client._generate_content("テストプロンプト", "claude-3-sonnet")
        
        assert result == ("レスポンスが空です", 100, 0)

    def test_generate_content_none_content(self):
        """Noneコンテンツ処理テスト"""
        client = ClaudeAPIClient()
        
        mock_usage = Mock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 0
        
        mock_response = Mock()
        mock_response.content = None  # Noneコンテンツ
        mock_response.usage = mock_usage
        
        mock_anthropic_client = Mock()
        mock_anthropic_client.messages.create.return_value = mock_response
        client.client = mock_anthropic_client
        
        result = client._generate_content("テストプロンプト", "claude-3-sonnet")
        
        assert result == ("レスポンスが空です", 100, 0)

    @patch('external_service.claude_api.CLAUDE_API_KEY', 'test_key')
    @patch('external_service.claude_api.CLAUDE_MODEL', 'claude-3-haiku')
    def test_integration_generate_summary(self):
        """統合テスト: generate_summaryメソッド"""
        client = ClaudeAPIClient()
        sample_medical_text = "患者情報のテストデータ"
        
        # 初期化のモック
        with patch.object(client, 'initialize', return_value=True):
            # プロンプト作成のモック
            with patch.object(client, 'create_summary_prompt') as mock_create_prompt:
                mock_create_prompt.return_value = "作成されたプロンプト"
                
                # モデル名取得のモック
                with patch.object(client, 'get_model_name') as mock_get_model:
                    mock_get_model.return_value = "claude-3-haiku"
                    
                    # コンテンツ生成のモック
                    with patch.object(client, '_generate_content') as mock_generate:
                        mock_generate.return_value = ("統合テスト結果", 200, 100)
                        
                        result = client.generate_summary(
                            medical_text=sample_medical_text,
                            additional_info="統合テスト追加情報",
                            department="統合テスト科",
                            document_type="統合テスト書類",
                            doctor="統合テスト医師"
                        )
                        
                        # 検証
                        assert result == ("統合テスト結果", 200, 100)
                        mock_create_prompt.assert_called_once_with(
                            sample_medical_text,
                            "統合テスト追加情報",
                            "統合テスト科",
                            "統合テスト書類",
                            "統合テスト医師"
                        )
                        mock_get_model.assert_called_once_with(
                            "統合テスト科", "統合テスト書類", "統合テスト医師"
                        )
                        mock_generate.assert_called_once_with(
                            "作成されたプロンプト", "claude-3-haiku"
                        )