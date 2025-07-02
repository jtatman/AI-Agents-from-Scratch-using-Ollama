# agents/__init__.py

from .summarize_tool import SummarizeTool
from .write_article_tool import WriteArticleTool
from .sanitize_data_tool import SanitizeDataTool
from .summarize_validator_agent import SummarizeValidatorAgent
from .write_article_validator_agent import WriteArticleValidatorAgent
from .sanitize_data_validator_agent import SanitizeDataValidatorAgent
from .refiner_agent import RefinerAgent # New import
from .validator_agent import ValidatorAgent  # New import
from .web_search_agent import WebSearchAgent
from .web_search_validator_agent import WebSearchValidatorAgent

class AgentManager:
    def __init__(self, max_retries=4, verbose=True):
        self.agents = {
            "summarize": SummarizeTool(max_retries=max_retries, verbose=verbose),
            "write_article": WriteArticleTool(max_retries=max_retries, verbose=verbose),
            "sanitize_data": SanitizeDataTool(max_retries=max_retries, verbose=verbose),
            "summarize_validator": SummarizeValidatorAgent(verbose=verbose),
            "write_article_validator": WriteArticleValidatorAgent(verbose=verbose),
            "sanitize_data_validator": SanitizeDataValidatorAgent(verbose=verbose),
            "refiner": RefinerAgent(max_retries=max_retries, verbose=verbose),     # New agent
            "validator": ValidatorAgent(max_retries=max_retries, verbose=verbose),   # New agent
            "web_search": WebSearchAgent(max_retries=max_retries, verbose=verbose),
            "web_search_validator": WebSearchValidatorAgent(verbose=verbose)
        }

    def get_agent(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return agent
