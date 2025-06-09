import pytest
from unittest.mock import Mock, patch
from typing import Tuple
from external_service.base_api import BaseAPIClient
from utils.exceptions import APIError


class MockableAPIClient(BaseAPIClient):
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
        client = MockableAPIClient("test_api_key", "test_model")
        assert client.api_key == "test_api_key"
        assert client.default_model == "test_model"

    @patch('external_service.base_api.get_config')
    @patch('external_service.base_api.get_prompt')
    def test_create_summary_prompt_with_default_prompt(self, mock_get_prompt, mock_get_config):
        """デフォルトプロンプトでサマリープロンプト作成テスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        # get_promptがNoneを返す（プロンプトデータなし）
        mock_get_prompt.return_value = None
        mock_get_config.return_value = {
            'PROMPTS': {
                'summary': 'デフォルトプロンプト: 以下の医療文書を要約してください。'
            }
        }

        client = MockableAPIClient()
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
    def test_create_summary_prompt_with_custom_prompt(self, mock_get_prompt):
        """カスタムプロンプトでサマリープロンプト作成テスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"
        mock_prompt_data = {
            'content': 'カスタムプロンプト: 特別な要約を作成してください。',
            'selected_model': 'custom-model-v1'
        }

        mock_get_prompt.return_value = mock_prompt_data

        client = MockableAPIClient()
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
    def test_get_model_name_with_custom_model(self, mock_get_prompt):
        """カスタムモデル名取得テスト"""
        # テストデータを直接定義
        mock_prompt_data = {
            'content': 'カスタムプロンプト',
            'selected_model': 'custom-model-v1'
        }

        mock_get_prompt.return_value = mock_prompt_data

        client = MockableAPIClient()
        model_name = client.get_model_name("内科", "診断書", "田中医師")

        assert model_name == mock_prompt_data['selected_model']

    @patch('external_service.base_api.get_prompt')
    def test_generate_summary_success(self, mock_get_prompt):
        """サマリー生成成功テスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        mock_get_prompt.return_value = None

        client = MockableAPIClient()

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
    def test_generate_summary_with_specified_model(self, mock_get_prompt):
        """指定モデルでのサマリー生成テスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        mock_get_prompt.return_value = None

        client = MockableAPIClient()

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

    def test_generate_summary_initialization_error(self):
        """初期化エラーのテスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        client = MockableAPIClient(api_key="")  # 空のAPIキー

        with pytest.raises(APIError, match="APIキーが設定されていません"):
            client.generate_summary(medical_text=sample_medical_text)

    def test_generate_summary_api_error_propagation(self):
        """APIErrorの伝播テスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        client = MockableAPIClient()

        with patch.object(client, '_generate_content') as mock_generate:
            mock_generate.side_effect = APIError("テスト用APIエラー")

            with pytest.raises(APIError, match="テスト用APIエラー"):
                client.generate_summary(medical_text=sample_medical_text)

    def test_generate_summary_generic_exception_handling(self):
        """一般的な例外のハンドリングテスト"""
        # テストデータを直接定義
        sample_medical_text = "患者情報のテストデータ"

        client = MockableAPIClient()

        with patch.object(client, '_generate_content') as mock_generate:
            mock_generate.side_effect = ValueError("予期しないエラー")

            with pytest.raises(APIError, match="MockableAPIClientでエラーが発生しました"):
                client.generate_summary(medical_text=sample_medical_text)
