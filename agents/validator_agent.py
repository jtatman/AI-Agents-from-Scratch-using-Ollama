# agents/validator_agent.py

from typing import Optional, Any
from pydantic import BaseModel
from .agent_base import AgentBase
import streamlit as st
from .openai_response import get_chat_response
from openai.types.chat import ChatCompletionMessageParam


class ValidatorAgent(AgentBase):
    def __init__(self, max_retries: int = 2, verbose: bool = True) -> None:
        super().__init__(name="ValidatorAgent", max_retries=max_retries, verbose=verbose)

    def execute(
        self, 
        topic: str, 
        article: str, 
        server_address: Optional[str] = None, 
        model_name: Optional[str] = None
    ) -> str:
        """Validate a research article for quality and academic standards using LLM."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an AI assistant that validates research articles for accuracy, completeness, and adherence to academic standards."},
            {"role": "user", "content": (
                "Given the topic and the research article below, assess whether the article comprehensively covers the topic, follows a logical structure, and maintains academic standards.\n"
                "Provide a brief analysis and rate the article on a scale of 1 to 5, where 5 indicates excellent quality.\n\n"
                f"Topic: {topic}\n\n"
                f"Article:\n{article}\n\n"
                "Validation:"
            )}
        ]
        try:
            if model_name is None:
                model_name = "deepseek-r1:1.5b"
            if self.verbose:
                print(f"[ValidatorAgent] Sending OpenAI request: model={model_name}, messages={messages}")
            response = get_chat_response(
                model=model_name,
                messages=messages,
                server_address=server_address,
                temperature=0.3,
                max_tokens=2049
            )
            validation = response.choices[0].message.content
            if self.verbose:
                print(f"[ValidatorAgent] OpenAI response: {validation}")
        except Exception as e:
            import traceback
            print(f"[ValidatorAgent] Exception: {e}")
            traceback.print_exc()
            raise RuntimeError(f"[ValidatorAgent] Failed to get response from OpenAI-compatible API: {e}")
        if not isinstance(validation, str):
            validation = ""
        return validation

'''
Herein lies a delimiter because pylint makes me sad...
'''

# Utility function for citation generation
def generate_citation(result: dict, style: str = "APA") -> str:
    """Generate a citation string from a paper result dict."""
    # Example expects keys: title, authors, year, url, journal (optional)
    authors = result.get("authors", [])
    if isinstance(authors, list):
        authors_str = ", ".join(authors)
    else:
        authors_str = str(authors)
    year = result.get("year", "n.d.")
    title = result.get("title", "")
    journal = result.get("journal", "")
    url = result.get("url", "")
    if style == "APA":
        citation = f"{authors_str} ({year}). {title}. {journal}. {url}"
    elif style == "BibTeX":
        citation = (
            f"@article{{{authors_str.replace(' ', '')}{year},\n"
            f"  title={{ {title} }},\n"
            f"  author={{ {authors_str} }},\n"
            f"  journal={{ {journal} }},\n"
            f"  year={{ {year} }},\n"
            f"  url={{ {url} }}\n}}"
        )
    else:
        citation = f"{authors_str} ({year}). {title}. {journal}. {url}"
    return citation


# --- Citation collection utility ---
# Note: This is a module-level function, not a method, so no 'self' is needed.
# Pylint warning can be ignored or suppressed for this function.

# pylint: disable=no-self-argument
def add_citation(result: dict) -> None:
    if "citations" not in st.session_state:
        st.session_state["citations"] = []
    citation = generate_citation(result)
    if citation not in st.session_state["citations"]:
        st.session_state["citations"].append(citation)