from scholarly import scholarly 

class GoogleScholarAgent:
    def __init__(self):
        pass

    def search(self, query):
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            for result in search_query:
                results.append({
                    "title": result.get("bib", {}).get("title"),
                    "authors": result.get("bib", {}).get("author"),
                    "abstract": result.get("bib", {}).get("abstract"),
                    "url": result.get("eprint_url") or result.get("pub_url"),
                })
            return results
        except Exception as e:
            raise RuntimeError(f"Google Scholar search failed: {e}")

''' scholarly example
from scholarly import scholarly

# Retrieve the author's data, fill-in, and print
# Get an iterator for the author results
search_query = scholarly.search_author('Steven A Cholewiak')
# Retrieve the first result from the iterator
first_author_result = next(search_query)
scholarly.pprint(first_author_result)

# Retrieve all the details for the author
author = scholarly.fill(first_author_result )
scholarly.pprint(author)

# Take a closer look at the first publication
first_publication = author['publications'][0]
first_publication_filled = scholarly.fill(first_publication)
scholarly.pprint(first_publication_filled)

# Print the titles of the author's publications
publication_titles = [pub['bib']['title'] for pub in author['publications']]
print(publication_titles)

# Which papers cited that publication?
citations = [citation['bib']['title'] for citation in scholarly.citedby(first_publication_filled)]
print(citations)
'''