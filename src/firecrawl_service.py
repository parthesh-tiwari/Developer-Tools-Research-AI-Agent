from firecrawl import FirecrawlApp
import os

class FireCrawlService:
    def __init__(self):
        FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

        if not FIRECRAWL_API_KEY:
            raise ValueError("API Key not found !!")
        self.app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    def search_companies(self, query: str, top_k: int = 5):
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=top_k,
                scrape_options={"formats": ["markdown"]}
            )
            print("Firecrawl crawled results : ")
            print(result)
            return result
        except Exception as e:
            print(e)
            class Dummy:
                data = []
            return Dummy()

    def scrape_company_pages(self, url: str):
        try:
            result = self.app.scrape(
                formats=["markdown"],
                url=url,
            )
            return result
        except Exception as e:
            print(e)
            return None
