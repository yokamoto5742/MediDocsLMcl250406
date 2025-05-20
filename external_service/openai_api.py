import os

from openai import OpenAI

from utils.config import OPENAI_API_KEY, OPENAI_MODEL, get_config
from utils.constants import MESSAGES
from utils.exceptions import APIError
from utils.prompt_manager import get_prompt_by_department


def initialize_openai():
    try:
        if OPENAI_API_KEY:
            return True
        else:
            raise APIError(MESSAGES["API_CREDENTIALS_MISSING"])
    except Exception as e:
        raise APIError(f"OpenAI API初期化エラー: {str(e)}")


def create_summary_prompt(medical_text, additional_info="", department="default", document_type="主治医意見書", doctor="default"):
    prompt_data = get_prompt_by_department(department, document_type, doctor)

    if not prompt_data:
        config = get_config()
        prompt_template = config['PROMPTS']['discharge_summary']
    else:
        prompt_template = prompt_data['content']

    prompt = f"{prompt_template}\n\n【カルテ情報】\n{medical_text}\n【追加情報】{additional_info}"
    return prompt


def openai_generate_summary(medical_text, additional_info="", department="default", document_type="主治医意見書",
                            doctor="default"):
    try:
        initialize_openai()
        prompt_data = get_prompt_by_department(department, document_type, doctor)
        model_name = prompt_data.get("selected_model") if prompt_data and prompt_data.get(
            "selected_model") else OPENAI_MODEL

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = create_summary_prompt(medical_text, additional_info, department, document_type, doctor)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "あなたは経験豊富な医療文書作成の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20000,
        )

        if response.choices and response.choices[0].message.content:
            summary_text = response.choices[0].message.content
        else:
            summary_text = "レスポンスが空でした"

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return summary_text, input_tokens, output_tokens

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"OpenAI APIでエラーが発生しました: {str(e)}")
