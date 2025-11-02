import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, V1ScrapeOptions

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

class FireCrawlService:

    def __init__(self):
        if not FIRECRAWL_API_KEY:
            raise ValueError("API Key not found !!")

        self.app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    def search_companies(self, query: str, top_k: int = 5):
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=top_k,
                scrape_options=V1ScrapeOptions(
                    formats=["markdown"]
                )
            )
            return result
        except Exception as e:
            print(e)
            return []

    def scrape_company_pages(self, url: str):
        try:
            result = self.app.scrape(
                formats=["markdown"],
                url=url,
            )

            return result

        except Exception as e:
            print(e)
            return []
