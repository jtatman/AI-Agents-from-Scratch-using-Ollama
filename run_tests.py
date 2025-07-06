import subprocess
import sys

class TestRunner:
    @staticmethod
    def run_tests():
        print("Running agent test suite...")
        result = subprocess.run([sys.executable, "-m", "unittest", "test_agent_suite.py"], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            print("All tests passed!")
        else:
            print("Some tests failed. See output above.")

if __name__ == "__main__":
    TestRunner.run_tests()
