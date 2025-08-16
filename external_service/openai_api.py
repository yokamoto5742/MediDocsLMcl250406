from openai import OpenAI
from typing import Tuple

from external_service.base_api import BaseAPIClient
from utils.config import OPENAI_API_KEY, OPENAI_MODEL
from utils.constants import MESSAGES
from utils.exceptions import APIError


class OpenAIAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(OPENAI_API_KEY, OPENAI_MODEL)
        self.client = None

    def initialize(self) -> bool:
        try:
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                return True
            else:
                raise APIError(MESSAGES["API_CREDENTIALS_MISSING"])
        except Exception as e:
            raise APIError(f"OpenAI API初期化エラー: {str(e)}")

    def _generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "あなたは経験豊富な医療文書作成の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=10000,
        )

        if response.choices and response.choices[0].message.content:
            summary_text = response.choices[0].message.content
        else:
            summary_text = "レスポンスが空です"

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return summary_text, input_tokens, output_tokens
