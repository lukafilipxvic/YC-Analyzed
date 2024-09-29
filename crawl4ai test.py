import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler

nest_asyncio.apply()
async def simple_crawl():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://www.ycombinator.com/companies/expand-ai",
    bypass_cache=True)
        print(result.markdown)
        print(result.cleaned_html)
        print(result.links)

if __name__=="__main__":
    asyncio.run(simple_crawl())