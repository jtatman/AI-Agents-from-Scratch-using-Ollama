# agents/summarize_validator_agent.py

from typing import Optional
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class SummarizeValidatorAgent:
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def execute(
        self,
        original_text: str,
        summary: str,
        server_address: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> str:
        """Validate summary using LLM."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an expert in scientific summary validation."},
            {"role": "user", "content": f"Validate the following summary:\n{summary}\n\nOriginal Text:\n{original_text}"}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[SummarizeValidatorAgent] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049,
            )
            validation = response.choices[0].message.content
            if self.verbose:
                print(f"[SummarizeValidatorAgent] OpenAI response: {validation}")
        except Exception as e:
            import traceback
            print(f"[SummarizeValidatorAgent] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[SummarizeValidatorAgent] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(validation, str):
            validation = ""
        return validation
