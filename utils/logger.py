# utils/logger.py

from loguru import logger
import sys
import os
import time
import psutil
from typing import Dict, Any
import json

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logger
logger.remove()  # Remove the default logger
logger.add(sys.stdout, level="INFO", format="<green>{time}</green> <level>{message}</level>")
logger.add("logs/multi_agent_system.log", rotation="1 MB", retention="10 days", level="DEBUG", format="{time} {level} {message}")

class PerformanceTracker:
    """Track performance metrics for agents and system operations"""
    
    def __init__(self):
        self.metrics = {
            "agent_executions": {},
            "execution_times": {},
            "token_usage": {},
            "success_rates": {},
            "system_metrics": {}
        }
        self.start_times = {}
    
    def start_tracking(self, operation_id: str, agent_name: str = None):
        """Start tracking an operation"""
        self.start_times[operation_id] = {
            "start_time": time.time(),
            "agent_name": agent_name or "unknown",
            "memory_before": psutil.virtual_memory().percent,
            "cpu_before": psutil.cpu_percent()
        }
        
        if agent_name:
            if agent_name not in self.metrics["agent_executions"]:
                self.metrics["agent_executions"][agent_name] = 0
            self.metrics["agent_executions"][agent_name] += 1
    
    def end_tracking(self, operation_id: str, success: bool = True, tokens_used: int = 0):
        """End tracking an operation and record metrics"""
        if operation_id not in self.start_times:
            return
        
        start_data = self.start_times[operation_id]
        execution_time = time.time() - start_data["start_time"]
        agent_name = start_data.get("agent_name", "unknown")
        
        # Record execution time
        if agent_name not in self.metrics["execution_times"]:
            self.metrics["execution_times"][agent_name] = []
        self.metrics["execution_times"][agent_name].append(execution_time)
        
        # Record token usage
        if tokens_used > 0:
            if agent_name not in self.metrics["token_usage"]:
                self.metrics["token_usage"][agent_name] = []
            self.metrics["token_usage"][agent_name].append(tokens_used)
        
        # Record success rate
        if agent_name not in self.metrics["success_rates"]:
            self.metrics["success_rates"][agent_name] = {"success": 0, "total": 0}
        self.metrics["success_rates"][agent_name]["total"] += 1
        if success:
            self.metrics["success_rates"][agent_name]["success"] += 1
        
        # Record system metrics
        current_memory = psutil.virtual_memory().percent
        current_cpu = psutil.cpu_percent()
        
        self.metrics["system_metrics"][operation_id] = {
            "execution_time": execution_time,
            "memory_usage": current_memory - start_data["memory_before"],
            "cpu_usage": current_cpu - start_data["cpu_before"],
            "success": success
        }
        
        # Clean up
        del self.start_times[operation_id]
        
        logger.info(f"Operation {operation_id} completed in {execution_time:.2f}s, Success: {success}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        processed_metrics = {
            "agent_executions": self.metrics["agent_executions"],
            "avg_execution_times": {},
            "avg_token_usage": {},
            "success_rates": {},
            "system_performance": self.metrics["system_metrics"]
        }
        
        # Calculate averages
        for agent, times in self.metrics["execution_times"].items():
            processed_metrics["avg_execution_times"][agent] = sum(times) / len(times) if times else 0
        
        for agent, tokens in self.metrics["token_usage"].items():
            processed_metrics["avg_token_usage"][agent] = sum(tokens) / len(tokens) if tokens else 0
        
        for agent, data in self.metrics["success_rates"].items():
            processed_metrics["success_rates"][agent] = data["success"] / data["total"] if data["total"] > 0 else 0
        
        return processed_metrics
    
    def save_metrics(self, filepath: str = "logs/performance_metrics.json"):
        """Save metrics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_metrics(), f, indent=2)

# Global performance tracker instance
performance_tracker = PerformanceTracker()
