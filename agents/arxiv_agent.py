import arxiv 

class ArxivAgent:
    def __init__(self):
        pass

    def search(self, query):
        try:
            search = arxiv.Search(
                query=query,
                max_results=10,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = []
            for result in search.results():
                results.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "url": result.entry_id
                })
            return results
        except Exception as e:
            raise RuntimeError(f"arXiv search failed: {e}")
