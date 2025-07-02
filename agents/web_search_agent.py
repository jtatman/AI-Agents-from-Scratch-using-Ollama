from typing import List, Dict, Optional
from pydantic import BaseModel
import requests

class WebSearchAgent(BaseModel):
    name: str = "WebSearchAgent"
    api_key: Optional[str] = None  # For engines like Serper or Tavily
    backend: str = "serper"  # or "tavily", "duckduckgo", etc.
    max_results: int = 10
    max_retries: int = 2
    verbose: bool = True

    def search(self, query: str) -> List[Dict]:
        """Search the web using the configured backend and return a list of results."""
        if self.backend == "serper":
            if not self.api_key:
                raise ValueError("Serper API key required.")
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            payload = {"q": query, "num": self.max_results}
            for attempt in range(self.max_retries):
                try:
                    resp = requests.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    results = []
                    for item in data.get("organic", []):
                        results.append({
                            "title": item.get("title"),
                            "url": item.get("link"),
                            "snippet": item.get("snippet"),
                            "source": "web"
                        })
                    if self.verbose:
                        print(f"[WebSearchAgent] Search results: {results}")
                    return results
                except Exception as e:
                    if self.verbose:
                        print(f"[WebSearchAgent] Attempt {attempt+1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
        # Add other backends as needed
        raise NotImplementedError(f"Backend {self.backend} not implemented.")
