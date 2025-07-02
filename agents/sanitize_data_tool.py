# agents/sanitize_data_agent.py

from typing import Optional
from pydantic import BaseModel
from .agent_base import AgentBase
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class SanitizeDataResult(BaseModel):
    sanitized_data: str

class SanitizeDataTool(AgentBase):
    def __init__(self, max_retries: int = 2, verbose: bool = True) -> None:
        super().__init__(name="SanitizeDataTool", max_retries=max_retries, verbose=verbose)

    def execute(
        self,
        text: str,
        server_address: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> SanitizeDataResult:
        """Sanitize the given data using LLM."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an expert in data sanitization."},
            {"role": "user", "content": f"Sanitize the following data:\n{text}"}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[SanitizeDataTool] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049,
            )
            sanitized_data = response.choices[0].message.content
            if self.verbose:
                print(f"[SanitizeDataTool] OpenAI response: {sanitized_data}")
        except Exception as e:
            import traceback
            print(f"[SanitizeDataTool] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[SanitizeDataTool] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(sanitized_data, str):
            sanitized_data = ""
        return SanitizeDataResult(sanitized_data=sanitized_data)
