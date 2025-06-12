import pytest
from unittest.mock import Mock, patch
from external_service.openai_api import OpenAIAPIClient
from utils.exceptions import APIError

@pytest.fixture
def sample_medical_text():
    """サンプルの医療テキスト"""
    return "患者は38歳男性で、胸痛を主訴として来院。心電図で異常所見なし。"

class TestOpenAIAPIClient:
    """OpenAIAPIClientクラスのテスト"""

    @patch('external_service.openai_api.OPENAI_API_KEY', 'test_openai_key')
    @patch('external_service.openai_api.OPENAI_MODEL', 'gpt-4')
    def test_init(self):
        """初期化テスト"""
        client = OpenAIAPIClient()
        assert client.api_key == 'test_openai_key'
        assert client.default_model == 'gpt-4'
        assert client.client is None

    @patch('external_service.openai_api.OPENAI_API_KEY', 'valid_openai_key')
    @patch('external_service.openai_api.OpenAI')
    def test_initialize_success(self, mock_openai):
        """正常な初期化テスト"""
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        
        client = OpenAIAPIClient()
        result = client.initialize()
        
        assert result is True
        assert client.client == mock_openai_instance
        mock_openai.assert_called_once_with(api_key='valid_openai_key')

    @patch('external_service.openai_api.OPENAI_API_KEY', '')
    def test_initialize_missing_api_key(self):
        """APIキー未設定時の初期化エラーテスト"""
        client = OpenAIAPIClient()

        with pytest.raises(APIError, match="OpenAI API初期化エラー:.*Gemini APIの認証情報が設定されていません"):
            client.initialize()

    @patch('external_service.openai_api.OPENAI_API_KEY', 'valid_openai_key')
    @patch('external_service.openai_api.OpenAI')
    def test_initialize_openai_error(self, mock_openai):
        """OpenAI初期化エラーテスト"""
        mock_openai.side_effect = Exception("認証エラー")
        
        client = OpenAIAPIClient()
        
        with pytest.raises(APIError, match="OpenAI API初期化エラー: 認証エラー"):
            client.initialize()

    def test_generate_content_success(self):
        """正常なコンテンツ生成テスト"""
        client = OpenAIAPIClient()
        
        # モックレスポンスの作成
        mock_message = Mock()
        mock_message.content = "OpenAIで生成されたサマリーテキスト"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 180
        mock_usage.completion_tokens = 90
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        
        # モッククライアントの設定
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_response
        client.client = mock_openai_client
        
        # テスト実行
        result = client._generate_content("OpenAIテストプロンプト", "gpt-4")
        
        # 検証
        assert result == ("OpenAIで生成されたサマリーテキスト", 180, 90)
        mock_openai_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは経験豊富な医療文書作成の専門家です。"},
                {"role": "user", "content": "OpenAIテストプロンプト"}
            ],
            max_tokens=10000,
        )

    def test_generate_content_empty_choices(self):
        """空のchoices処理テスト"""
        client = OpenAIAPIClient()
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 0
        
        mock_response = Mock()
        mock_response.choices = []  # 空のchoices
        mock_response.usage = mock_usage
        
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_response
        client.client = mock_openai_client
        
        result = client._generate_content("テストプロンプト", "gpt-4")
        
        assert result == ("レスポンスが空です", 100, 0)

    def test_generate_content_none_choices(self):
        """Nonechoices処理テスト"""
        client = OpenAIAPIClient()
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 0
        
        mock_response = Mock()
        mock_response.choices = None  # Nonechoices
        mock_response.usage = mock_usage
        
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_response
        client.client = mock_openai_client
        
        result = client._generate_content("テストプロンプト", "gpt-4")
        
        assert result == ("レスポンスが空です", 100, 0)

    def test_generate_content_empty_message_content(self):
        """空のメッセージコンテンツ処理テスト"""
        client = OpenAIAPIClient()
        
        mock_message = Mock()
        mock_message.content = ""  # 空のコンテンツ
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 0
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_response
        client.client = mock_openai_client
        
        result = client._generate_content("テストプロンプト", "gpt-4")
        
        assert result == ("レスポンスが空です", 100, 0)

    def test_generate_content_none_message_content(self):
        """Noneメッセージコンテンツ処理テスト"""
        client = OpenAIAPIClient()
        
        mock_message = Mock()
        mock_message.content = None  # Noneコンテンツ
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 0
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create.return_value = mock_response
        client.client = mock_openai_client
        
        result = client._generate_content("テストプロンプト", "gpt-4")
        
        assert result == ("レスポンスが空です", 100, 0)

    @patch('external_service.openai_api.OPENAI_API_KEY', 'test_key')
    @patch('external_service.openai_api.OPENAI_MODEL', 'gpt-3.5-turbo')
    def test_integration_generate_summary(self, sample_medical_text):
        """統合テスト: generate_summaryメソッド"""
        client = OpenAIAPIClient()
        
        # 初期化のモック
        with patch.object(client, 'initialize', return_value=True):
            # プロンプト作成のモック
            with patch.object(client, 'create_summary_prompt') as mock_create_prompt:
                mock_create_prompt.return_value = "OpenAI用プロンプト"
                
                # モデル名取得のモック
                with patch.object(client, 'get_model_name') as mock_get_model:
                    mock_get_model.return_value = "gpt-3.5-turbo"
                    
                    # コンテンツ生成のモック
                    with patch.object(client, '_generate_content') as mock_generate:
                        mock_generate.return_value = ("OpenAI統合テスト結果", 250, 125)
                        
                        result = client.generate_summary(
                            medical_text=sample_medical_text,
                            additional_info="OpenAI追加情報",
                            department="OpenAI科",
                            document_type="OpenAI書類",
                            doctor="OpenAI医師",
                            model_name="gpt-4"  # 明示的なモデル指定
                        )
                        
                        # 検証
                        assert result == ("OpenAI統合テスト結果", 250, 125)
                        mock_create_prompt.assert_called_once_with(
                            sample_medical_text,
                            "OpenAI追加情報",
                            "OpenAI科",
                            "OpenAI書類",
                            "OpenAI医師"
                        )
                        # model_nameが明示的に指定されているため、get_model_nameは呼ばれない
                        mock_get_model.assert_not_called()
                        mock_generate.assert_called_once_with(
                            "OpenAI用プロンプト", "gpt-4"
                        )