import unittest
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel

# Pydantic models for test results
class SummaryResult(BaseModel):
    summary: str

class SanitizedResult(BaseModel):
    sanitized: str

class ArticleResult(BaseModel):
    article: str

# Configure your Ollama-compatible endpoint (see README from amitness/ollama-remote)
MODEL = "deepseek-r1:1.5b"
BASE_URL = "http://localhost:11434/v1"  # adjust for cloudflared or remote
API_KEY = "ollama"  # OpenAI key ignored for local; use "ollama" convention

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

class TestModelCompletions(unittest.TestCase):
    def test_chat_completion(self):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Summarize AI in one sentence."}
            ]
        )
        message: Optional[str] = response.choices[0].message.content
        self.assertIsNotNone(message)
        summary_result = SummaryResult(summary=message or "")
        self.assertIsInstance(summary_result.summary, str)
        self.assertGreater(len(summary_result.summary), 10)
        print("\nSummary:", summary_result.summary)

    def test_sanitize_data(self):
        prompt = "Sanitize the following: Patient John Doe, born 1970, was admitted to General Hospital."
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You redact private health information."},
                {"role": "user", "content": prompt}
            ]
        )
        result: Optional[str] = response.choices[0].message.content
        self.assertIsNotNone(result)
        sanitized_result = SanitizedResult(sanitized=result or "")
        self.assertNotIn("John Doe", sanitized_result.sanitized)
        print("\nSanitized:", sanitized_result.sanitized)

    def test_generate_article(self):
        topic = "AI in Healthcare"
        outline = "Introduction, Applications, Challenges"
        prompt = f"Write an article titled '{topic}' with the following outline: {outline}"
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        article: Optional[str] = response.choices[0].message.content
        self.assertIsNotNone(article)
        article_result = ArticleResult(article=article or "")
        self.assertIsInstance(article_result.article, str)
        self.assertIn("AI", article_result.article)
        print("\nGenerated Article:\n", article_result.article)

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        import traceback
        print("\nTest suite failed with exception:")
        traceback.print_exc()
