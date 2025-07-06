# openai_response.py
"""
Micro-library for OpenAI/Ollama chat completions using OpenAI >=1.0 syntax.
Additional Ollama compatibility with custom base_url
"""
from typing import Iterable, Any, Optional
from openai.types.chat import ChatCompletionMessageParam
from openai import OpenAI

def get_chat_response(
    model: str,
    messages: Iterable[ChatCompletionMessageParam],
    server_address: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Calls the OpenAI/Ollama chat completions endpoint using the new 1.0+ syntax.
    Args:
        model (str): The model name (e.g., 'deepseek-r1:1.5b').
        messages (Iterable[ChatCompletionMessageParam]): List of message dicts (role/content pairs).
        server_address (str, optional): Ollama server base URL (e.g., 'http://localhost:11434').
        **kwargs: Additional parameters (temperature, max_tokens, etc).
    Returns:
        The full response object (not just the text).
    """
    base_url = (server_address.rstrip("/") + "/v1") if server_address else "http://localhost:11434/v1"
    client = OpenAI(
        base_url=base_url,
        api_key="ollama"  # required, but unused for Ollama
    )
    response = client.chat.completions.create(
        model=model,
        messages=list(messages),
        **kwargs
    )
    return response
