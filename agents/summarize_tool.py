# agents/summarize_agent.py

from typing import List, Optional
from pydantic import BaseModel
from .agent_base import AgentBase
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class SummarizeResult(BaseModel):
    summary: str
    

class SummarizeTool(AgentBase):
    def __init__(self, max_retries: int = 2, verbose: bool = True) -> None:
        super().__init__(name="SummarizeTool", max_retries=max_retries, verbose=verbose)

    def execute(
        self,
        text: str,
        server_address: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> SummarizeResult:
        """Summarize the given text using LLM."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an expert scientific summarizer."},
            {"role": "user", "content": f"Summarize the following text:\n{text}"}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[SummarizeTool] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049,
            )
            summary = response.choices[0].message.content
            if self.verbose:
                print(f"[SummarizeTool] OpenAI response: {summary}")
        except Exception as e:
            import traceback
            print(f"[SummarizeTool] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[SummarizeTool] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(summary, str):
            summary = ""
        return SummarizeResult(summary=summary)
