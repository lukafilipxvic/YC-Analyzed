import os
import argparse
from pydantic import ValidationError
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LXMLWebScrapingStrategy
from litellm import completion
import instructor
import pandas as pd
import csv
import asyncio

from tools.extract import extract_company_details

COMPANY_HEADER = "Name,Batch,Status,Industry,Team Size,Location\n"
FOUNDER_HEADER = "Name,Batch,Status,Industry,Team Size,Location,Founder's First Name,Founder's Last Name,Founder's LinkedIn,Founder's Twitter\n"

def setup_file_paths(date=None):
    if date:
        directory = f'data/{date}'
        Companies_file_path = f"data/{date}/YC_Companies.csv"
        Founders_file_path = f"data/{date}/YC_Founders.csv"
        URL_file_path = f"data/{date}/YC_URLs.csv"
    else:
        directory = 'data/'
        Companies_file_path = "data/YC_Companies.csv"
        Founders_file_path = "data/YC_Founders.csv"
        URL_file_path = "data/YC_URLs.csv"
    os.makedirs(directory, exist_ok=True)
    return Companies_file_path, Founders_file_path, URL_file_path

def get_last_processed_company(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_line = next(reader, None)
            if first_line is None:
                return -1
            if "name" in first_line[0].lower() and "status" in first_line[1].lower():
                unique_companies = {tuple(row[:5]) for row in reader if row and len(row) >= 5}
            else:
                unique_companies = {tuple(first_line[:5])}
                unique_companies.update(tuple(row[:5]) for row in reader if row and len(row) >= 5)
            return len(unique_companies)
    except FileNotFoundError:
        return -1

async def main():
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    Companies_file_path, Founders_file_path, YC_URL_file_path = setup_file_paths(date)
    df = pd.read_csv(YC_URL_file_path)

    # Create files if they don't exist.
    if not os.path.exists(Companies_file_path):
        with open(Companies_file_path, 'w', encoding='utf-8') as company_list:
            pass
    if not os.path.exists(Founders_file_path):
        with open(Founders_file_path, 'w', encoding='utf-8') as founder_list:
            pass

    completed_company_count = get_last_processed_company(Companies_file_path)
    print(f"Companies processed so far: {completed_company_count}", flush=True)

    client = instructor.from_litellm(completion)

    # Crawl4ai setup
    browser_conf = BrowserConfig(headless=False)
    session_id = "yc_page_session"
    crawler_conf = CrawlerRunConfig(only_text=True,
                              cache_mode=CacheMode.ENABLED,
                              exclude_external_images=True,
                              excluded_tags=["header", "footer"],
                              session_id=session_id,
                              scraping_strategy=LXMLWebScrapingStrategy())

    # Open the output files once.
    with open(Companies_file_path, 'a', encoding='utf-8') as company_list, \
         open(Founders_file_path, 'a', encoding='utf-8') as founder_list:
        if completed_company_count == -1:
            company_list.write(COMPANY_HEADER)
            founder_list.write(FOUNDER_HEADER)

        # Loop over each URL in the CSV.
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            for index, row in df.iterrows():
                if index < completed_company_count - 1:
                    continue

                company_url = row['YC URL']
                print(f"({index + 1}/{len(df)}) Extracting {company_url}...", flush=True)
                try:
                    result = await crawler.arun(url=company_url, config=crawler_conf)
                    if result.markdown is None:
                        continue

                    company_extract = extract_company_details(client, result.markdown, model="openai/gpt-4o-mini")
                    
                    # Write company data.
                    company_list.write(
                        f'"{company_extract.get("name")}",{company_extract.get("batch")},'
                        f'{company_extract.get("status")},"{company_extract.get("industry")}",'
                        f'{company_extract.get("team_size")},{company_extract.get("city")}\n'
                    )
                    
                    if company_extract.get("founders") is not None:
                        for founder in company_extract["founders"]:
                            founder_list.write(
                                f'"{company_extract.get("name")}",{company_extract.get("batch")},'
                                f'{company_extract.get("status")},"{company_extract.get("industry")}",'
                                f'{company_extract.get("team_size")},{company_extract.get("city")},'
                                f'{founder.get("first_name")},{founder.get("last_name")},'
                                f'{founder.get("founder_linkedin_url", "")},{founder.get("founder_twitter_url", "")}\n'
                            )
                except ValidationError as e:
                    print(f"Validation error for {company_url}: {e}", flush=True)
        await crawler.crawler_strategy.kill_session(session_id)

    print(f"Data saved to {Companies_file_path} and {Founders_file_path}", flush=True)

if __name__ == "__main__":
    # Run the async main function.
    asyncio.run(main())
