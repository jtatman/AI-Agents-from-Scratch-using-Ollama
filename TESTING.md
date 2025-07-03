# README: Agent Test Suite

## How to Run All Tests

1. Make sure your Ollama server is running and accessible at the correct address (default: http://10.209.1.96:11434) and the model (default: gemma3:4b) is available.
2. Install all requirements:

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

3. Run the test suite:

    python run_tests.py

This will run all agent and validator tests and print results to the console.

## Customizing Server/Model

Edit `test_agent_suite.py` and change the `SERVER` and `MODEL` variables if needed.

## Adding More Tests

Add new test methods to `test_agent_suite.py` following the unittest style.

---

If any test fails, check the Ollama server logs and the printed error output for details.
