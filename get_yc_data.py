from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from get_urls import get_all_urls
from language_model import extract_urls, extract_company_details


def scrape_individual_yc_company_page(company_url: str):
    driver = webdriver.Chrome()
    driver.get(company_url)
    
    # Use WebDriverWait instead of sleep
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

    # Scroll to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
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

def scrape_yc_batch(batch_code: str):
    all_urls = get_all_urls(batch_code=batch_code) # Returns all links from the page
    yc_company_urls = extract_urls(input=all_urls) # Returns company_path extract (low tokens)
    yc_company_urls['Company_path'] = [f"https://www.ycombinator.com/{url}" for url in yc_company_urls['Company_path']] # Where needed, add the full URL
    print(yc_company_urls)
    print(len(yc_company_urls['Company_path']))

    with open(f'yc_data/YC_Companies_{batch_code}.csv', 'w', encoding='utf-8') as file:  # Open a file to save details
        # Write header based on the company data structure
        file.write("Name,Status,Batch,Team_size,Website,Founders\n")  # Write header

        for index, company_url in enumerate(yc_company_urls['Company_path'], start=1):
            count = f"({index}/{len(yc_company_urls['Company_path'])})"
            print(f"{count} Extracting {company_url}...") 
            company_yc_page = scrape_individual_yc_company_page(company_url=company_url)
            
            print("Page extract complete.")
            
            print(f"{count} Extracting YC company details...")
            company_details = extract_company_details(company_yc_page)
            print(f"{count} YC page extraction complete.")
            
            # Format the company details for CSV
            founders = "; ".join([f"{f['name']} ({f.get('Founder_linkedin_url', '')} {f.get('Founder_twitter_url', '')})" for f in company_details['Founders']])
            file.write(f"{company_details['Name']},{company_details['Status']},{company_details['Batch']},{company_details['Team_size']},{company_details['Website']},{founders}\n")  # Save company details to the file


# Scrape by batch usage
if __name__ == "__main__":
    batch_codes=["W18", "S18", "W19", "S19", "W20", "S20", "W21", "S21", "S22", "W23", "S23", "W24", "S24", "W15", "W16", "S16"]
    for batch in batch_codes:
        print(f"Scraping YC batch {batch}...")
        scrape_yc_batch(batch_code=batch)

            # Get the company's current global google trends score, use the peak of ChatGPT, Facebook or YouTube as 100 points.
            # Search the internet to get their current annual revenue/valuation.