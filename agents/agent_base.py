# agents/agent_base.py

import ollama
from abc import ABC, abstractmethod
from loguru import logger
import os
import uuid
import time
from typing import Dict, Any, Optional
from utils.config import config_manager, AgentConfig
from utils.logger import performance_tracker

class AgentBase(ABC):
    def __init__(self, name: str, max_retries: int = 2, verbose: bool = True, config_override: Optional[AgentConfig] = None):
        self.name = name
        self.verbose = verbose
        
        # Load configuration
        if config_override:
            self.config = config_override
        else:
            self.config = config_manager.get_agent_config(name.replace("Tool", "").replace("Agent", "").lower())
        
        # Override with constructor parameters if provided
        if max_retries != 2:  # If explicitly provided
            self.config.max_retries = max_retries
        
        self.max_retries = self.config.max_retries

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def call_llama(self, messages, temperature: Optional[float] = None, max_tokens: Optional[int] = None, operation_id: Optional[str] = None):
        """
        Calls the Llama model via Ollama and retrieves the response.

        Args:
            messages (list): A list of message dictionaries.
            temperature (float): Sampling temperature (uses config default if None).
            max_tokens (int): Maximum number of tokens in the response (uses config default if None).
            operation_id (str): Unique identifier for this operation (for tracking).

        Returns:
            str: The content of the model's response.
        """
        # Use config defaults if not provided
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        operation_id = operation_id or str(uuid.uuid4())
        
        # Start performance tracking
        performance_tracker.start_tracking(operation_id, self.name)
        
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                if self.verbose:
                    logger.info(f"[{self.name}] Sending messages to Ollama (model: {self.config.model}, temp: {temperature}, max_tokens: {max_tokens})")
                    for msg in messages:
                        logger.debug(f"  {msg['role']}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                
                start_time = time.time()
                
                # Call the Ollama chat API
                response = ollama.chat(
                    model=self.config.model,
                    messages=messages,
                    options={
                        'temperature': temperature,
                        'num_predict': max_tokens,
                    }
                )
                
                # Parse the response to extract the text content
                reply = response['message']['content']
                
                # Estimate token usage (rough approximation)
                estimated_tokens = len(reply.split()) * 1.3  # Rough estimation
                
                execution_time = time.time() - start_time
                
                if self.verbose:
                    logger.info(f"[{self.name}] Received response in {execution_time:.2f}s (approx {estimated_tokens:.0f} tokens)")
                    logger.debug(f"  Response: {reply[:100]}{'...' if len(reply) > 100 else ''}")
                
                # End performance tracking
                performance_tracker.end_tracking(operation_id, success=True, tokens_used=int(estimated_tokens))
                
                return reply
                
            except Exception as e:
                retries += 1
                last_error = e
                logger.error(f"[{self.name}] Error during Ollama call: {e}. Retry {retries}/{self.max_retries}")
                
                if retries < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** retries
                    logger.info(f"[{self.name}] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        # End performance tracking with failure
        performance_tracker.end_tracking(operation_id, success=False)
        
        raise Exception(f"[{self.name}] Failed to get response from Ollama after {self.max_retries} retries. Last error: {last_error}")

    def update_config(self, new_config: AgentConfig):
        """Update the agent's configuration"""
        self.config = new_config
        self.max_retries = new_config.max_retries
        config_manager.update_agent_config(self.name.replace("Tool", "").replace("Agent", "").lower(), new_config)
        
        if self.verbose:
            logger.info(f"[{self.name}] Configuration updated")

    def get_config(self) -> AgentConfig:
        """Get the agent's current configuration"""
        return self.config

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent"""
        all_metrics = performance_tracker.get_metrics()
        agent_metrics = {}
        
        # Filter metrics for this agent
        for metric_type, data in all_metrics.items():
            if metric_type == "system_performance":
                continue
            
            if isinstance(data, dict) and self.name in data:
                agent_metrics[metric_type] = data[self.name]
        
        return agent_metrics

    def validate_input(self, input_data: Any) -> bool:
        """Basic input validation - can be overridden by subclasses"""
        if input_data is None:
            return False
        if isinstance(input_data, str) and len(input_data.strip()) == 0:
            return False
        return True

    def prepare_system_message(self, custom_prompt: Optional[str] = None) -> Dict[str, str]:
        """Prepare the system message for the LLM"""
        prompt = custom_prompt or self.config.system_prompt
        return {"role": "system", "content": prompt}
