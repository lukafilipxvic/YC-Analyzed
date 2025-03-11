from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LXMLWebScrapingStrategy
import asyncio

browser_conf = BrowserConfig(browser_type="firefox",headless=True)
crawler_conf = CrawlerRunConfig(#cache_mode=CacheMode.DISABLED,
                                #exclude_external_images=True,
                                #excluded_tags=["header", "footer"],
                                magic=True,
                                page_timeout=60000,
                                simulate_user=True,
                                scan_full_page=True,
                                scroll_delay=0.4,
                                scraping_strategy=LXMLWebScrapingStrategy(),
                                wait_for=""
                                )

async def main():
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(url="https://www.ycombinator.com/companies?batch=S06" , config=crawler_conf)
        if result.success:
            #print(result.html)          # Raw HTML
            #print(result.cleaned_html)  # Cleaned HTML 
            #print(result.markdown)      # Print clean markdown content
            #print(result.fit_markdown)  # Most relevant content in markdown
            print(result.links)
        else:
            print("Error:", result.error_message)

if __name__=="__main__":
    asyncio.run(main())