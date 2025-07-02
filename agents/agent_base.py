# agents/agent_base.py

import os
from pydantic import BaseModel, Field
from loguru import logger
import openai

class AgentBase(BaseModel):
    name: str
    max_retries: int = 2
    verbose: bool = True
    server_address: str = Field(default_factory=lambda: os.environ.get("OLLAMA_SERVER", "http://localhost:11434/v1"))
    model_name: str = Field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b"))
    api_key: str = Field(default_factory=lambda: os.environ.get("OLLAMA_API_KEY", "ollama"))
    client: openai.OpenAI = Field(default_factory=lambda: openai.OpenAI(
        base_url=os.environ.get("OLLAMA_SERVER", "http://localhost:11434/v1"),
        api_key=os.environ.get("OLLAMA_API_KEY", "ollama")
    ))

    model_config = {
        "arbitrary_types_allowed": True
    }
