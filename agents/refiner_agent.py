# agents/refiner_agent.py

from typing import Optional
from .agent_base import AgentBase
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class RefinerAgent(AgentBase):
    def __init__(self, max_retries: int = 2, verbose: bool = True) -> None:
        super().__init__(name="RefinerAgent", max_retries=max_retries, verbose=verbose)

    def execute(
        self,
        text: str,
        server_address: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> str:
        """Refine a scientific article using LLM."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an expert scientific article refiner."},
            {"role": "user", "content": f"Refine the following article:\n{text}"}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[RefinerAgent] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049,
            )
            refined_article = response.choices[0].message.content
            if self.verbose:
                print(f"[RefinerAgent] OpenAI response: {refined_article}")
        except Exception as e:
            import traceback
            print(f"[RefinerAgent] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[RefinerAgent] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(refined_article, str):
            refined_article = ""
        return refined_article
