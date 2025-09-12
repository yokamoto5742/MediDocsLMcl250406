import os

from anthropic import AnthropicBedrock
from dotenv import load_dotenv
from typing import Tuple

from external_service.base_api import BaseAPIClient
from utils.constants import MESSAGES
from utils.exceptions import APIError

load_dotenv()


class ClaudeAPIClient(BaseAPIClient):
    def __init__(self):
        # AWS認証情報を環境変数から取得
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL")

        # 親クラスの初期化（API_KEYはNoneを渡し、モデル名はANTHROPIC_MODELを使用）
        super().__init__(None, self.anthropic_model)
        self.client = None

    def initialize(self) -> bool:
        try:
            # AWS認証情報の確認
            if not all([self.aws_access_key_id, self.aws_secret_access_key, self.aws_region]):
                raise APIError("AWS認証情報が設定されていません。環境変数を確認してください。")

            if not self.anthropic_model:
                raise APIError("ANTHROPIC_MODELが設定されていません。環境変数を確認してください。")

            # AnthropicBedrockクライアントの初期化
            self.client = AnthropicBedrock(
                aws_access_key=self.aws_access_key_id,
                aws_secret_key=self.aws_secret_access_key,
                aws_region=self.aws_region,
            )
            return True

        except Exception as e:
            raise APIError(f"Amazon Bedrock Claude API初期化エラー: {str(e)}")

    def _generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        """
        プロンプトから要約を生成します。
        Args:
            prompt: 生成用プロンプト
            model_name: 使用するモデル名（実際にはself.anthropic_modelを使用）
        Returns:
            Tuple[str, int, int]: (生成された要約, 入力トークン数, 出力トークン数)
        Raises:
            APIError: API呼び出しに失敗した場合
        """
        try:
            # Amazon BedrockのClaude APIを呼び出し
            # model_nameパラメータは親クラスとの互換性のために受け取るが、
            # 実際はself.anthropic_modelを使用
            response = self.client.messages.create(
                model=self.anthropic_model,
                max_tokens=6000,  # 最大出力トークン数
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # レスポンスから要約テキストを取得
            if response.content:
                summary_text = response.content[0].text
            else:
                summary_text = MESSAGES["EMPTY_RESPONSE"]

            # トークン使用量を取得
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return summary_text, input_tokens, output_tokens

        except Exception as e:
            raise APIError(MESSAGES["BEDROCK_API_ERROR"].format(error=str(e)))