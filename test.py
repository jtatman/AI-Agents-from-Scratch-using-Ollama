# test.py - Comprehensive Test Suite for Enhanced Multi-Agent AI System

import ollama
import unittest
import json
import time
import sys
import os
from typing import Dict, Any

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import AgentManager
from utils.logger import logger, performance_tracker
from utils.config import config_manager, AgentConfig, AppConfig
from utils.export_manager import export_manager

class TestAgentSystem(unittest.TestCase):
    """Test suite for the enhanced multi-agent AI system"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.agent_manager = AgentManager(max_retries=1, verbose=False)
        
        # Test data
        cls.sample_medical_text = """
        Patient is a 45-year-old male presenting with chest pain and shortness of breath. 
        He has a history of hypertension and diabetes. Current medications include metformin 500mg twice daily 
        and lisinopril 10mg daily. Vital signs show BP 150/90, HR 95, RR 18, O2 sat 97%.
        Physical examination reveals clear lungs and regular heart rhythm.
        Assessment: Possible angina. Plan: ECG, cardiac enzymes, stress test.
        """
        
        cls.sample_clinical_note = """
        CHIEF COMPLAINT: Chest pain
        
        HISTORY OF PRESENT ILLNESS: 
        45-year-old male presents with acute onset chest pain, 8/10 severity, 
        radiating to left arm. Started 2 hours ago.
        
        PAST MEDICAL HISTORY: 
        Hypertension, Type 2 diabetes mellitus
        
        MEDICATIONS: 
        Metformin 500mg BID, Lisinopril 10mg daily
        
        ALLERGIES: NKDA
        
        PHYSICAL EXAM:
        Vital signs: BP 150/90, HR 95, RR 18, Temp 98.6F, O2 sat 97%
        Heart: Regular rhythm, no murmur
        Lungs: Clear bilaterally
        
        ASSESSMENT AND PLAN:
        1. Chest pain - rule out ACS
           - ECG
           - Cardiac enzymes
           - Cardiology consult
        """
        
        cls.sample_phi_data = """
        Patient John Doe (DOB: 01/15/1978, SSN: 123-45-6789) visited on 03/15/2024.
        Address: 123 Main St, Anytown, ST 12345. Phone: (555) 123-4567.
        Diagnosis: Hypertension. Treatment plan discussed.
        """

    def test_ollama_connection(self):
        """Test basic Ollama connectivity"""
        try:
            response = ollama.chat(model='llama3.2:3b', messages=[
                {'role': 'user', 'content': 'Say "test successful"'}
            ])
            self.assertIn('successful', response['message']['content'].lower())
            logger.info("✅ Ollama connection test passed")
        except Exception as e:
            self.fail(f"Ollama connection failed: {e}")

    def test_agent_manager_initialization(self):
        """Test agent manager initialization"""
        agents = self.agent_manager.get_all_agents()
        expected_agents = [
            'summarize', 'write_article', 'sanitize_data', 'clinical_parser',
            'summarize_validator', 'write_article_validator', 
            'sanitize_data_validator', 'clinical_parser_validator',
            'refiner', 'validator'
        ]
        
        for agent_name in expected_agents:
            self.assertIn(agent_name, agents)
        
        logger.info("✅ Agent Manager initialization test passed")

    def test_configuration_system(self):
        """Test configuration management"""
        # Test app config
        app_config = config_manager.get_app_config()
        self.assertIsInstance(app_config, AppConfig)
        self.assertIn('llama3.2:3b', app_config.available_models)
        
        # Test agent config
        summarize_config = config_manager.get_agent_config('summarize')
        self.assertIsInstance(summarize_config, AgentConfig)
        self.assertGreater(summarize_config.max_tokens, 0)
        
        # Test config updates
        original_temp = summarize_config.temperature
        new_config = AgentConfig(temperature=0.9, max_tokens=400)
        config_manager.update_agent_config('summarize', new_config)
        updated_config = config_manager.get_agent_config('summarize')
        self.assertEqual(updated_config.temperature, 0.9)
        
        # Restore original
        summarize_config.temperature = original_temp
        config_manager.update_agent_config('summarize', summarize_config)
        
        logger.info("✅ Configuration system test passed")

    def test_performance_tracking(self):
        """Test performance monitoring"""
        # Start tracking
        operation_id = "test_operation_123"
        performance_tracker.start_tracking(operation_id, "TestAgent")
        
        # Simulate work
        time.sleep(0.1)
        
        # End tracking
        performance_tracker.end_tracking(operation_id, success=True, tokens_used=100)
        
        # Check metrics
        metrics = performance_tracker.get_metrics()
        self.assertIn("TestAgent", metrics["agent_executions"])
        self.assertEqual(metrics["agent_executions"]["TestAgent"], 1)
        
        logger.info("✅ Performance tracking test passed")

    def test_medical_summarization(self):
        """Test medical text summarization"""
        try:
            summarize_agent = self.agent_manager.get_agent("summarize")
            summary = summarize_agent.execute(self.sample_medical_text)
            
            self.assertIsInstance(summary, str)
            self.assertGreater(len(summary), 10)
            self.assertLess(len(summary), len(self.sample_medical_text))
            
            logger.info("✅ Medical summarization test passed")
        except Exception as e:
            self.fail(f"Medical summarization failed: {e}")

    def test_clinical_parser(self):
        """Test clinical note parsing"""
        try:
            clinical_agent = self.agent_manager.get_agent("clinical_parser")
            
            # Test full parsing
            parsed_data = clinical_agent.execute(self.sample_clinical_note)
            self.assertIsInstance(parsed_data, dict)
            self.assertIn("chief_complaint", parsed_data)
            self.assertIn("medications", parsed_data)
            self.assertIn("metadata", parsed_data)
            
            # Test entity extraction
            entities = clinical_agent.extract_medical_entities(self.sample_clinical_note)
            self.assertIsInstance(entities, dict)
            self.assertIn("symptoms", entities)
            self.assertIn("medications", entities)
            
            # Test medical summary
            summary = clinical_agent.generate_medical_summary(self.sample_clinical_note)
            self.assertIsInstance(summary, str)
            self.assertGreater(len(summary), 20)
            
            logger.info("✅ Clinical parser test passed")
        except Exception as e:
            self.fail(f"Clinical parser failed: {e}")

    def test_data_sanitization(self):
        """Test PHI data sanitization"""
        try:
            sanitize_agent = self.agent_manager.get_agent("sanitize_data")
            sanitized = sanitize_agent.execute(self.sample_phi_data)
            
            self.assertIsInstance(sanitized, str)
            self.assertNotIn("John Doe", sanitized)
            self.assertNotIn("123-45-6789", sanitized)
            self.assertNotIn("(555) 123-4567", sanitized)
            
            logger.info("✅ Data sanitization test passed")
        except Exception as e:
            self.fail(f"Data sanitization failed: {e}")

    def test_validation_agents(self):
        """Test validation agents"""
        try:
            # Test summarize validator
            summarize_agent = self.agent_manager.get_agent("summarize")
            validator_agent = self.agent_manager.get_agent("summarize_validator")
            
            summary = summarize_agent.execute(self.sample_medical_text)
            validation = validator_agent.execute(
                original_text=self.sample_medical_text, 
                summary=summary
            )
            
            self.assertIsInstance(validation, str)
            self.assertGreater(len(validation), 10)
            
            logger.info("✅ Validation agents test passed")
        except Exception as e:
            self.fail(f"Validation agents failed: {e}")

    def test_export_functionality(self):
        """Test export functionality"""
        try:
            test_data = {
                "test_key": "test_value",
                "nested": {"inner": "data"},
                "list": ["item1", "item2"]
            }
            
            # Test JSON export
            json_path = export_manager.export_to_json(test_data, "test_export.json")
            self.assertTrue(os.path.exists(json_path))
            
            # Test CSV export
            csv_path = export_manager.export_to_csv(test_data, "test_export.csv")
            self.assertTrue(os.path.exists(csv_path))
            
            # Test export string generation
            json_string = export_manager.get_export_string(test_data, "json")
            self.assertIn("test_value", json_string)
            
            # Cleanup
            if os.path.exists(json_path):
                os.remove(json_path)
            if os.path.exists(csv_path):
                os.remove(csv_path)
            
            logger.info("✅ Export functionality test passed")
        except Exception as e:
            self.fail(f"Export functionality failed: {e}")

    def test_agent_base_functionality(self):
        """Test base agent functionality"""
        try:
            agent = self.agent_manager.get_agent("summarize")
            
            # Test config retrieval
            config = agent.get_config()
            self.assertIsInstance(config, AgentConfig)
            
            # Test input validation
            self.assertTrue(agent.validate_input("Valid input"))
            self.assertFalse(agent.validate_input(""))
            self.assertFalse(agent.validate_input(None))
            
            # Test system message preparation
            system_msg = agent.prepare_system_message()
            self.assertIsInstance(system_msg, dict)
            self.assertEqual(system_msg["role"], "system")
            
            logger.info("✅ Agent base functionality test passed")
        except Exception as e:
            self.fail(f"Agent base functionality failed: {e}")

    def test_error_handling(self):
        """Test error handling and recovery"""
        try:
            # Test invalid agent request
            with self.assertRaises(ValueError):
                self.agent_manager.get_agent("nonexistent_agent")
            
            # Test invalid input handling
            summarize_agent = self.agent_manager.get_agent("summarize")
            with self.assertRaises(ValueError):
                summarize_agent.execute("")
            
            logger.info("✅ Error handling test passed")
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")

def run_basic_functionality_test():
    """Run a basic functionality test without unittest framework"""
    print("🚀 Running Basic Functionality Test...\n")
    
    try:
        # Test Ollama connection
        print("1. Testing Ollama connection...")
        response = ollama.chat(model='llama3.2:3b', messages=[
            {'role': 'user', 'content': 'Respond with exactly: CONNECTION_TEST_SUCCESS'}
        ])
        assert 'CONNECTION_TEST_SUCCESS' in response['message']['content']
        print("   ✅ Ollama connection successful\n")
        
        # Test agent manager
        print("2. Testing Agent Manager...")
        manager = AgentManager(max_retries=1, verbose=False)
        agents = manager.get_agent_list()
        print(f"   ✅ {len(agents)} agents loaded: {', '.join(agents[:3])}...\n")
        
        # Test configuration system
        print("3. Testing Configuration System...")
        app_config = config_manager.get_app_config()
        print(f"   ✅ Default model: {app_config.default_model}")
        print(f"   ✅ Available models: {len(app_config.available_models)}\n")
        
        # Test summarization
        print("4. Testing Medical Summarization...")
        summarize_agent = manager.get_agent("summarize")
        test_text = "Patient presents with chest pain and shortness of breath. History of hypertension."
        summary = summarize_agent.execute(test_text)
        print(f"   ✅ Summary generated ({len(summary)} chars)\n")
        
        # Test clinical parser
        print("5. Testing Clinical Parser...")
        clinical_agent = manager.get_agent("clinical_parser")
        test_note = "CHIEF COMPLAINT: Chest pain. MEDICATIONS: Lisinopril 10mg daily. ASSESSMENT: Possible angina."
        entities = clinical_agent.extract_medical_entities(test_note)
        print(f"   ✅ Entities extracted: {len(entities)} categories\n")
        
        # Test performance tracking
        print("6. Testing Performance Tracking...")
        metrics = performance_tracker.get_metrics()
        executions = sum(metrics.get("agent_executions", {}).values())
        print(f"   ✅ Performance metrics tracked: {executions} total executions\n")
        
        print("🎉 All basic functionality tests passed!\n")
        print("=" * 60)
        print("✅ System is ready for use!")
        print("   Run: streamlit run app.py")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check if llama3.2:3b model is available: ollama list")
        print("3. Install missing dependencies: pip install -r requirements.txt")
        return False

def run_performance_benchmark():
    """Run performance benchmarks"""
    print("\n🏃 Running Performance Benchmarks...\n")
    
    manager = AgentManager(max_retries=1, verbose=False)
    test_text = "Patient presents with acute chest pain, shortness of breath, and sweating. Medical history includes hypertension and diabetes."
    
    # Benchmark summarization
    print("Benchmarking Summarization Agent...")
    start_time = time.time()
    for i in range(3):
        summarize_agent = manager.get_agent("summarize")
        summary = summarize_agent.execute(test_text)
    avg_time = (time.time() - start_time) / 3
    print(f"   Average time: {avg_time:.2f}s per summarization\n")
    
    # Benchmark clinical parser
    print("Benchmarking Clinical Parser...")
    start_time = time.time()
    for i in range(3):
        clinical_agent = manager.get_agent("clinical_parser")
        entities = clinical_agent.extract_medical_entities(test_text)
    avg_time = (time.time() - start_time) / 3
    print(f"   Average time: {avg_time:.2f}s per entity extraction\n")
    
    # Display metrics
    metrics = performance_tracker.get_metrics()
    print("Performance Summary:")
    print(f"   Total agent executions: {sum(metrics.get('agent_executions', {}).values())}")
    if metrics.get('avg_execution_times'):
        avg_times = list(metrics['avg_execution_times'].values())
        print(f"   Average execution time: {sum(avg_times)/len(avg_times):.2f}s")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the Enhanced Multi-Agent AI System")
    parser.add_argument("--mode", choices=["basic", "full", "benchmark"], default="basic",
                       help="Test mode: basic (quick test), full (comprehensive), benchmark (performance)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.mode == "basic":
        success = run_basic_functionality_test()
        if not success:
            sys.exit(1)
    elif args.mode == "benchmark":
        run_basic_functionality_test()
        run_performance_benchmark()
    else:  # full
        print("🧪 Running Comprehensive Test Suite...\n")
        unittest.main(argv=[''], exit=False, verbosity=2 if args.verbose else 1)
        run_performance_benchmark()