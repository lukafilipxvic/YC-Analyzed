import os
import argparse
from bs4 import BeautifulSoup
import csv
from markdownify import markdownify as md
import pandas as pd
from pydantic import ValidationError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.web_driver import setup_driver, scroll_to_bottom
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
        Founders_file_path = f"data/YC_Founders.csv"
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

def scrape_individual_yc_company_page(driver, company_url: str):
    driver.get(company_url)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    scroll_to_bottom(driver, scroll_pause=0.2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_content_div = soup.find('div', {'data-page': True})
    
    if page_content_div:
        company_data = page_content_div["data-page"]
        company_data_md = md(str(company_data))
        print(company_data_md)

        links = [a['href'] for a in page_content_div.find_all('a', href=True)]
        links = [link for link in links if not link.startswith("/")]
        return company_data_md, links
    else:
        print("Page content div not found.")
        return None, None

def main():
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    Companies_file_path, Founders_file_path, YC_URL_file_path = setup_file_paths(date)
    df = pd.read_csv(YC_URL_file_path)

    if not os.path.exists(Companies_file_path):
        with open(Companies_file_path, 'w', encoding='utf-8') as company_list:
            pass

    if not os.path.exists(Founders_file_path):
        with open(Founders_file_path, 'w', encoding='utf-8') as founder_list:
            pass

    completed_company_count = get_last_processed_company(Companies_file_path)
    print(completed_company_count)

    driver = setup_driver()

    try:
        with open(Companies_file_path, 'a', encoding='utf-8') as company_list:
            if completed_company_count == -1:
                company_list.write(COMPANY_HEADER)

            with open(Founders_file_path, 'a', encoding='utf-8') as founder_list:
                if completed_company_count == -1:
                    founder_list.write(FOUNDER_HEADER)

                for index, row in df.iterrows():
                    if index < completed_company_count-1:
                        continue

                    company_url = row['YC URL']
                    print(f"({index + 1}/{len(df)}) Extracting {company_url}...")

                    try:
                        company_yc_page = scrape_individual_yc_company_page(driver, company_url)
                        company_extract = extract_company_details(company_yc_page, model="groq/llama-3.3-70b-specdec")
                        
                        company_list.write(
                                    f'"{company_extract.get('name')}",{company_extract.get('batch')},{company_extract.get('status')},'
                                    f'"{company_extract.get('industry')}",{company_extract.get('team_size')},{company_extract.get('city')}\n'
                        )
                    except ValidationError as e:
                        print(f"Validation error for {company_url}: {e}")
                    if company_extract["founders"] is not None:
                        for founder in company_extract["founders"]:
                                founder_list.write(
                                    f'"{company_extract.get('name')}",{company_extract.get('batch')},{company_extract.get('status')},'
                                    f'"{company_extract.get('industry')}",{company_extract.get('team_size')},{company_extract.get('city')},'
                                    f'{founder.get('first_name')},{founder.get('last_name')},'
                                    f'{founder.get('founder_linkedin_url', '')},{founder.get('founder_twitter_url', '')}\n'
                                )

        print(f"Data saved to {Companies_file_path} and {Founders_file_path}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

# Get the company's current global google trends score, use the peak of ChatGPT, Facebook or YouTube as 100 points.
# Search the internet to get their current annual revenue/valuation?
