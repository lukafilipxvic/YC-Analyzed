from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

from src.data_pipeline.get_yc_urls import get_all_urls
from src.llm import extract_urls, extract_company_details


def scrape_individual_yc_company_page(company_url: str):
    with sync_playwright() as p:  # Use Playwright context
        browser = p.chromium.launch()  # Launch the browser
        page = browser.new_page()
        page.goto(company_url)
        
        # Wait for the page to load
        page.wait_for_selector("a")  # Wait for any anchor tag to be present

        # Scroll to the bottom of the page
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(page.content(), 'html.parser')  # Use page.content() instead of driver.page_source
        # Find the div with data-page attribute
        page_content_div = soup.find('div', {'data-page': True})
        if page_content_div:
            # Extract the text content and links from the div
            page_content = page_content_div.get_text()
            links = [a['href'] for a in page_content_div.find_all('a', href=True)]
            return page_content, links
        else:
            print("Page content div not found.")
            return None, None
        
        browser.close()

def scrape_yc_batch(batch_code: str):
    all_urls = get_all_urls(batch_code=batch_code)
    yc_company_urls = extract_urls(input=all_urls)

    with open(f'data/YC_{batch_code}.csv', 'w') as file:  # Open a file to save details
        # Write header based on the company data structure
        file.write("Name,Status,Batch,Team_size,One_liner,Website,Founders\n")  # Write header

        for company_url in yc_company_urls['Company_path']:
            print(f"Extracting {company_url}...")
            company_yc_page = scrape_individual_yc_company_page(company_url=company_url)
            print("Page extract complete.")
            
            print(f"Extracting YC company details...")
            company_details = extract_company_details(company_yc_page)
            print(f"YC page extraction complete.")
            
            # Format the company details for CSV
            founders = "; ".join([f"{f['name']} ({f.get('Founder_linkedin_url', '')} {f.get('Founder_twitter_url', '')})" for f in company_details['Founders']])
            one_liner = company_details['One_liner'].replace(',', '') # for safety of the csv file.
            file.write(f"{company_details['Name']},{company_details['Status']},{company_details['Batch']},{company_details['Team_size']},{one_liner},{company_details['Website']},{founders}\n")  # Save company details to the file


# Example usage
if __name__ == "__main__":
    batch_codes=["S05", "W06", "S06", "W07", "S07", "W08", "S08", "W09", "S09", "W10", "S10", "W11", "S11"]
    for batch in batch_codes:
        print(f"Scraping Batch {batch}...")
        scrape_yc_batch(batch_code=batch)

# Get the company's current global google trends score, use the peak of ChatGPT, Facebook or YouTube as 100 points.
# Search the internet to get their current annual revenue/valuation.