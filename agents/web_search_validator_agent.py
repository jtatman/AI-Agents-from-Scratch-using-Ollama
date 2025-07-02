class WebSearchValidatorAgent:
    def __init__(self):
        pass

    def validate(self, results):
        try:
            if not results:
                raise ValueError("No results to validate.")

            validated_results = []
            for result in results:
                if "title" in result and "url" in result:
                    validated_results.append(result)
                else:
                    raise ValueError("Invalid result format: Missing title or URL.")

            return validated_results
        except Exception as e:
            raise RuntimeError(f"Validation failed: {e}")
