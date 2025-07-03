from typing import List, Dict, Optional
from pydantic import BaseModel
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam

class WebSearchValidatorAgent(BaseModel):
    name: str = "WebSearchValidatorAgent"
    model_name: str = "deepseek-r1:1.5b"
    server_address: Optional[str] = None
    max_results: int = 10
    verbose: bool = True

    def validate(self, results: List[Dict]) -> List[Dict]:
        """Validate/filter web search results for scientific/technical relevance using LLM."""
        validated = []
        for result in results:
            system_message = (
                "You are a scientific research assistant. Given a web search result, determine if it is likely to be a scientific paper, journal article, technical blog, or credible technology news. Reply VALID or INVALID."
            )
            user_content = f"Title: {result.get('title','')}\nSnippet: {result.get('snippet','')}\nURL: {result.get('url','')}"
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ]
            response = get_chat_response(
                model=self.model_name,
                messages=messages,
                server_address=self.server_address,
                temperature=0.0,
                max_tokens=16,
            )
            verdict = response.choices[0].message.content
            if verdict and "VALID" in verdict.upper():
                validated.append(result)
            if len(validated) >= self.max_results:
                break
        return validated
