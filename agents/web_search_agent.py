import requests 

class WebSearchAgent:
    def __init__(self):
        self.base_url = "https://api.scholarsearch.com"  # Hypothetical API for scholarly web search

    def search(self, query):
        try:
            response = requests.get(f"{self.base_url}/search", params={"q": query})
            response.raise_for_status()
            results = response.json()
            return [
                {
                    "title": result.get("title"),
                    "author": result.get("author"),
                    "abstract": result.get("abstract"),
                    "url": result.get("url")
                }
                for result in results.get("papers", [])
            ]
        except Exception as e:
            raise RuntimeError(f"Web search failed: {e}")
