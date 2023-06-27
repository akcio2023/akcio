import os
import sys
from typing import Optional, Union, Tuple

from langchain.chat_models import ChatOpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import chat_configs

chat_configs = chat_configs['openai']
llm_kwargs = chat_configs.get('llm_kwargs', {})


class ChatLLM(ChatOpenAI):
    '''Chat with LLM given context. Must be a LangChain BaseLanguageModel to adapt agent.'''
    model_name: str = chat_configs.get('openai_model', 'gpt-3.5-turbo')
    openai_api_key: Optional[str] = chat_configs.get('openai_api_key', None)
    temperature: float = llm_kwargs.get('temperature', 0.0)
    openai_organization: Optional[str] = llm_kwargs.get('openai_organization', None)
    streaming: bool = llm_kwargs.get('streaming', False)
    n: int = llm_kwargs.get('n', 1)
    max_tokens: Optional[int] = llm_kwargs.get('max_tokens', None)
