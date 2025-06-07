import pytest
from unittest.mock import Mock, patch
from typing import Tuple
from external_service.base_api import BaseAPIClient
from utils.exceptions import APIError


class TestableAPIClient(BaseAPIClient):
    """テスト用のBaseAPIClient具象実装クラス"""
    
    def __init__(self, api_key="test_key", default_model="test_model"):
        super().__init__(api_key, default_model)
        self.initialized = False
        self.generate_content_called = False
    
    def initialize(self) -> bool:
        if not self.api_key:
            raise APIError("APIキーが設定されていません")
        self.initialized = True
        return True
    
    def _generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        if not self.initialized:
            raise APIError("クライアントが初期化されていません")
        self.generate_content_called = True
        return f"Generated content for: {prompt[:20]}...", 100, 50


class TestBaseAPIClient:
    """BaseAPIClientクラスのテスト"""

    def test_init(self):
        """初期化テスト"""
        client = TestableAPIClient("test_api_key", "test_model")
        assert client.api_key == "test_api_key"
        assert client.default_model == "test_model"

    @patch('external_service.base_api.get_config')
    @patch('external_service.base_api.get_prompt')
    def test_create_summary_prompt_with_default_prompt(self, mock_get_prompt, mock_get_config, sample_medical_text):
        """デフォルトプロンプトでサマリープロンプト作成テスト"""
        # get_promptがNoneを返す（プロンプトデータなし）
        mock_get_prompt.return_value = None
        mock_get_config.return_value = {
            'PROMPTS': {
                'summary': 'デフォルトプロンプト: 以下の医療文書を要約してください。'
            }
        }
        
        client = TestableAPIClient()
        prompt = client.create_summary_prompt(
            medical_text=sample_medical_text,
            additional_info="追加情報テスト",
            department="内科",
            document_type="診断書",
            doctor="田中医師"
        )
        
        expected_prompt = (
            "デフォルトプロンプト: 以下の医療文書を要約してください。\n\n"
            f"【カルテ情報】\n{sample_medical_text}\n"
            "【追加情報】追加情報テスト"
        )
        
        assert prompt == expected_prompt
        mock_get_prompt.assert_called_once_with("内科", "診断書", "田中医師")

    @patch('external_service.base_api.get_prompt')
    def test_create_summary_prompt_with_custom_prompt(self, mock_get_prompt, sample_medical_text, mock_prompt_data):
        """カスタムプロンプトでサマリープロンプト作成テスト"""
        mock_get_prompt.return_value = mock_prompt_data
        
        client = TestableAPIClient()
        prompt = client.create_summary_prompt(
            medical_text=sample_medical_text,
            additional_info="",
            department="外科",
            document_type="手術記録",
            doctor="佐藤医師"
        )
        
        expected_prompt = (
            f"{mock_prompt_data['content']}\n\n"
            f"【カルテ情報】\n{sample_medical_text}\n"
            "【追加情報】"
        )
        
        assert prompt == expected_prompt

    @patch('external_service.base_api.get_prompt')
    def test_get_model_name_with_custom_model(self, mock_get_prompt, mock_prompt_data):
        """カスタムモデル名取得テスト"""
        mock_get_prompt.return_value = mock_prompt_data
        
        client = TestableAPIClient()
        model_name = client.get_model_name("内科", "診断書", "田中医師")
        
        assert model_name == mock_prompt_data['selected_model']

    @patch('external_service.base_api.get_prompt')
    def test_get_model_name_with_default_model(self, mock_get_prompt):
        """デフォルトモデル名取得テスト"""
        mock_get_prompt.return_value = None
        
        client = TestableAPIClient(default_model="default_model")
        model_name = client.get_model_name("内科", "診断書", "田中医師")
        
        assert model_name == "default_model"

    @patch('external_service.base_api.get_prompt')
    def test_get_model_name_with_prompt_data_but_no_model(self, mock_get_prompt):
        """プロンプトデータがあるがモデル指定がない場合のテスト"""
        mock_get_prompt.return_value = {'content': 'test'}  # selected_modelなし
        
        client = TestableAPIClient(default_model="fallback_model")
        model_name = client.get_model_name("内科", "診断書", "田中医師")
        
        assert model_name == "fallback_model"

    @patch('external_service.base_api.get_prompt')
    def test_generate_summary_success(self, mock_get_prompt, sample_medical_text):
        """サマリー生成成功テスト"""
        mock_get_prompt.return_value = None
        
        client = TestableAPIClient()
        
        with patch.object(client, 'create_summary_prompt') as mock_create_prompt:
            mock_create_prompt.return_value = "テストプロンプト"
            
            result = client.generate_summary(
                medical_text=sample_medical_text,
                additional_info="追加情報",
                department="内科",
                document_type="診断書",
                doctor="田中医師"
            )
            
            assert result == ("Generated content for: テストプロンプト...", 100, 50)
            assert client.initialized
            assert client.generate_content_called

    @patch('external_service.base_api.get_prompt')
    def test_generate_summary_with_specified_model(self, mock_get_prompt, sample_medical_text):
        """指定モデルでのサマリー生成テスト"""
        mock_get_prompt.return_value = None
        
        client = TestableAPIClient()
        
        with patch.object(client, '_generate_content') as mock_generate:
            mock_generate.return_value = ("指定モデル結果", 120, 60)
            
            result = client.generate_summary(
                medical_text=sample_medical_text,
                model_name="specified_model"
            )
            
            mock_generate.assert_called_once()
            args = mock_generate.call_args[0]
            assert args[1] == "specified_model"  # model_name引数の確認
            assert result == ("指定モデル結果", 120, 60)

    def test_generate_summary_initialization_error(self, sample_medical_text):
        """初期化エラーのテスト"""
        client = TestableAPIClient(api_key="")  # 空のAPIキー
        
        with pytest.raises(APIError, match="APIキーが設定されていません"):
            client.generate_summary(medical_text=sample_medical_text)

    def test_generate_summary_api_error_propagation(self, sample_medical_text):
        """APIErrorの伝播テスト"""
        client = TestableAPIClient()
        
        with patch.object(client, '_generate_content') as mock_generate:
            mock_generate.side_effect = APIError("テスト用APIエラー")
            
            with pytest.raises(APIError, match="テスト用APIエラー"):
                client.generate_summary(medical_text=sample_medical_text)

    def test_generate_summary_generic_exception_handling(self, sample_medical_text):
        """一般的な例外のハンドリングテスト"""
        client = TestableAPIClient()
        
        with patch.object(client, '_generate_content') as mock_generate:
            mock_generate.side_effect = ValueError("予期しないエラー")
            
            with pytest.raises(APIError, match="TestableAPIClientでエラーが発生しました"):
                client.generate_summary(medical_text=sample_medical_text)