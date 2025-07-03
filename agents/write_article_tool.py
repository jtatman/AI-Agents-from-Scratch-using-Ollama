# agents/write_article_agent.py

from typing import Optional
from pydantic import BaseModel
from .agent_base import AgentBase
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class WriteArticleResult(BaseModel):
    article: str

class WriteArticleTool(AgentBase):
    def __init__(self, max_retries: int = 2, verbose: bool = True) -> None:
        super().__init__(name="WriteArticleTool", max_retries=max_retries, verbose=verbose)

    def execute(
        self, 
        topic: str, 
        outline: Optional[str] = None, 
        server_address: Optional[str] = None, 
        model_name: Optional[str] = None
    ) -> WriteArticleResult:
        """Generate a research article on the given topic and outline using LLM."""
        system_message = "You are an expert academic writer."
        user_content = f"Write a research article on the following topic:\nTopic: {topic}\n\n"
        if outline:
            user_content += f"Outline:\n{outline}\n\n"
        user_content += "Article:\n"
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[WriteArticleTool] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049,
            )
            article = response.choices[0].message.content
            if self.verbose:
                print(f"[WriteArticleTool] OpenAI response: {article}")
        except Exception as e:
            import traceback
            print(f"[WriteArticleTool] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[WriteArticleTool] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(article, str):
            article = ""
        return WriteArticleResult(article=article)
