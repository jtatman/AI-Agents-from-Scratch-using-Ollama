import configparser
import os
from typing import Dict, Any, List
import json
from dataclasses import dataclass, asdict, field

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    temperature: float = 0.7
    max_tokens: int = 500
    model: str = "llama3.2:3b"
    system_prompt: str = ""
    max_retries: int = 2
    timeout: int = 30

@dataclass
class AppConfig:
    """Main application configuration"""
    default_model: str = "llama3.2:3b"
    available_models: List[str] = field(default_factory=lambda: [
        "llama3.2:3b", 
        "llama3.2:1b", 
        "llama3.1:8b",
        "gemma2:2b",
        "phi3:mini"
    ])
    theme: str = "light"
    export_format: str = "json"
    enable_metrics: bool = True
    log_level: str = "INFO"

class ConfigManager:
    """Manage application and agent configurations"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Default configurations
        self.app_config = AppConfig()
        self.agent_configs = {
            "summarize": AgentConfig(
                system_prompt="You are an AI assistant that summarizes medical texts concisely and accurately.",
                max_tokens=300
            ),
            "write_article": AgentConfig(
                system_prompt="You are an AI assistant that writes research articles with proper structure and citations.",
                max_tokens=800,
                temperature=0.8
            ),
            "sanitize_data": AgentConfig(
                system_prompt="You are an AI assistant that removes PHI from medical data while preserving clinical value.",
                max_tokens=600
            ),
            "refiner": AgentConfig(
                system_prompt="You are an AI assistant that enhances and refines academic writing.",
                max_tokens=1000,
                temperature=0.6
            ),
            "clinical_parser": AgentConfig(
                system_prompt="You are an AI assistant that parses clinical notes and extracts structured medical information.",
                max_tokens=500
            )
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                
                # Load app config
                if 'APP' in self.config:
                    app_section = self.config['APP']
                    self.app_config.default_model = app_section.get('default_model', self.app_config.default_model)
                    self.app_config.theme = app_section.get('theme', self.app_config.theme)
                    self.app_config.export_format = app_section.get('export_format', self.app_config.export_format)
                    self.app_config.enable_metrics = app_section.getboolean('enable_metrics', self.app_config.enable_metrics)
                    self.app_config.log_level = app_section.get('log_level', self.app_config.log_level)
                    
                    # Load available models
                    models_str = app_section.get('available_models', '')
                    if models_str:
                        self.app_config.available_models = [m.strip() for m in models_str.split(',')]
                
                # Load agent configs
                for agent_name in self.agent_configs:
                    if agent_name.upper() in self.config:
                        agent_section = self.config[agent_name.upper()]
                        agent_config = self.agent_configs[agent_name]
                        
                        agent_config.temperature = agent_section.getfloat('temperature', agent_config.temperature)
                        agent_config.max_tokens = agent_section.getint('max_tokens', agent_config.max_tokens)
                        agent_config.model = agent_section.get('model', agent_config.model)
                        agent_config.system_prompt = agent_section.get('system_prompt', agent_config.system_prompt)
                        agent_config.max_retries = agent_section.getint('max_retries', agent_config.max_retries)
                        agent_config.timeout = agent_section.getint('timeout', agent_config.timeout)
                        
            except Exception as e:
                print(f"Error loading config: {e}")
                self.save_config()  # Save default config
        else:
            self.save_config()  # Create default config file
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Clear existing config
            self.config.clear()
            
            # Save app config
            self.config['APP'] = {
                'default_model': self.app_config.default_model,
                'available_models': ','.join(self.app_config.available_models),
                'theme': self.app_config.theme,
                'export_format': self.app_config.export_format,
                'enable_metrics': str(self.app_config.enable_metrics),
                'log_level': self.app_config.log_level
            }
            
            # Save agent configs
            for agent_name, agent_config in self.agent_configs.items():
                section_name = agent_name.upper()
                self.config[section_name] = {
                    'temperature': str(agent_config.temperature),
                    'max_tokens': str(agent_config.max_tokens),
                    'model': agent_config.model,
                    'system_prompt': agent_config.system_prompt,
                    'max_retries': str(agent_config.max_retries),
                    'timeout': str(agent_config.timeout)
                }
            
            with open(self.config_file, 'w') as f:
                self.config.write(f)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for a specific agent"""
        return self.agent_configs.get(agent_name, AgentConfig())
    
    def update_agent_config(self, agent_name: str, config: AgentConfig):
        """Update configuration for a specific agent"""
        self.agent_configs[agent_name] = config
        self.save_config()
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration"""
        return self.app_config
    
    def update_app_config(self, config: AppConfig):
        """Update application configuration"""
        self.app_config = config
        self.save_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all configurations to dictionary"""
        return {
            'app': asdict(self.app_config),
            'agents': {name: asdict(config) for name, config in self.agent_configs.items()}
        }
    
    def from_dict(self, config_dict: Dict[str, Any]):
        """Load configurations from dictionary"""
        if 'app' in config_dict:
            app_data = config_dict['app']
            self.app_config = AppConfig(**app_data)
        
        if 'agents' in config_dict:
            for agent_name, agent_data in config_dict['agents'].items():
                self.agent_configs[agent_name] = AgentConfig(**agent_data)
        
        self.save_config()

# Global config manager instance
config_manager = ConfigManager()