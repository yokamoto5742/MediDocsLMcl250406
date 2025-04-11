import os
import anthropic
from anthropic import Anthropic

from utils.config import get_config, CLAUDE_API_KEY, CLAUDE_MODEL
from utils.constants import MESSAGES
from utils.prompt_manager import get_prompt_by_department
from utils.exceptions import APIError


def initialize_claude():
    """
    Claude APIを初期化する関数
    
    Returns:
        bool: 初期化が成功したかどうか
        
    Raises:
        APIError: 初期化に失敗した場合
    """
    try:
        if CLAUDE_API_KEY:
            return True
        else:
            raise APIError(MESSAGES["API_CREDENTIALS_MISSING"])
    except Exception as e:
        raise APIError(f"Claude API初期化エラー: {str(e)}")


def create_discharge_summary_prompt(medical_text, department="default"):
    """
    退院時サマリ作成用のプロンプトを作成する
    
    Args:
        medical_text (str): 医療テキストデータ
        department (str, optional): 診療科. デフォルトは "default"
        
    Returns:
        str: 作成されたプロンプト
    """
    prompt_data = get_prompt_by_department(department)

    if not prompt_data:
        config = get_config()
        prompt_template = config['PROMPTS']['discharge_summary']
    else:
        prompt_template = prompt_data['content']

    prompt = f"{prompt_template}\n\n【カルテ情報】\n{medical_text}"
    return prompt


def generate_discharge_summary(medical_text, department="default"):
    """
    Claude APIを使用して退院時サマリを生成する関数
    
    Args:
        medical_text (str): 医療テキストデータ
        department (str, optional): 診療科. デフォルトは "default"
        
    Returns:
        str: 生成された退院時サマリ
        
    Raises:
        APIError: API呼び出しに失敗した場合
    """
    try:
        initialize_claude()
        model_name = CLAUDE_MODEL
        client = Anthropic(api_key=CLAUDE_API_KEY)

        prompt = create_discharge_summary_prompt(medical_text, department)
        
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # レスポンスからテキストを抽出
        if response.content:
            summary_text = response.content[0].text
        else:
            summary_text = "レスポンスが空でした"

        return summary_text

    except APIError as e:
        raise e
    except Exception as e:
        raise APIError(f"Claude APIでエラーが発生しました: {str(e)}")
