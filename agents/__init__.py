# agents/__init__.py

from .summarize_tool import SummarizeTool
from .write_article_tool import WriteArticleTool
from .sanitize_data_tool import SanitizeDataTool
from .clinical_parser_tool import ClinicalParserTool
from .summarize_validator_agent import SummarizeValidatorAgent
from .write_article_validator_agent import WriteArticleValidatorAgent
from .sanitize_data_validator_agent import SanitizeDataValidatorAgent
from .clinical_parser_validator_agent import ClinicalParserValidatorAgent
from .refiner_agent import RefinerAgent
from .validator_agent import ValidatorAgent

class AgentManager:
    def __init__(self, max_retries=2, verbose=True):
        self.agents = {
            "summarize": SummarizeTool(max_retries=max_retries, verbose=verbose),
            "write_article": WriteArticleTool(max_retries=max_retries, verbose=verbose),
            "sanitize_data": SanitizeDataTool(max_retries=max_retries, verbose=verbose),
            "clinical_parser": ClinicalParserTool(max_retries=max_retries, verbose=verbose),
            "summarize_validator": SummarizeValidatorAgent(max_retries=max_retries, verbose=verbose),
            "write_article_validator": WriteArticleValidatorAgent(max_retries=max_retries, verbose=verbose),
            "sanitize_data_validator": SanitizeDataValidatorAgent(max_retries=max_retries, verbose=verbose),
            "clinical_parser_validator": ClinicalParserValidatorAgent(max_retries=max_retries, verbose=verbose),
            "refiner": RefinerAgent(max_retries=max_retries, verbose=verbose),
            "validator": ValidatorAgent(max_retries=max_retries, verbose=verbose)
        }

    def get_agent(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return agent
    
    def get_all_agents(self):
        """Get all available agents"""
        return self.agents
    
    def get_agent_list(self):
        """Get list of agent names"""
        return list(self.agents.keys())
