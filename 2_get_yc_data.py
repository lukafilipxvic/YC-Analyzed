from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from markdownify import markdownify as md

from get_urls import get_all_urls
from language_model import extract_urls, extract_company_details
import pandas as pd

def scrape_individual_yc_company_page(company_url: str):
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable image loading
        "profile.managed_default_content_settings.plugins": 2  # Disable video loading
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(company_url)
    
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

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_content_div = soup.find('div', {'data-page': True})
      
    if page_content_div:
        page_content = page_content_div.get_text()
        page_content_md = md(str(page_content))

        links = [a['href'] for a in page_content_div.find_all('a', href=True)]
        links = [link for link in links if not link.startswith("/")]
        return page_content_md, links
    else:
        print("Page content div not found.")
        return None, None

def scrape_yc_batch(batch_code: str): # Scrape by batch
    all_urls = get_all_urls(batch_code=batch_code)
    #yc_company_urls = extract_urls(input=all_urls) # Returns company_path extract (low tokens)
    #yc_company_urls['Company_path'] = [f"https://www.ycombinator.com/companies/{url}" for url in yc_company_urls['Company_path']]
    #print(yc_company_urls)
    #print(len(yc_company_urls['Company_path']))

    with open(f'yc_data/YC_Companies_{batch_code}.csv', 'w', encoding='utf-8') as file:
        file.write("Name,Status,Batch,Team_size,Website\n")  # Write header

        for index, company_url in enumerate(all_urls, start=1): # If extracting using llm, replace all_urls with yc_company_urls['Company_path'] 
            count = f"({index}/{len(all_urls)})" 
            print(f"{count} Extracting {company_url}...") 
            company_yc_page = scrape_individual_yc_company_page(company_url=company_url)
            
            print("Page extract complete.")
            
            print(f"{count} Extracting YC company details...")
            company_details = extract_company_details(company_yc_page)
            print(f"{count} YC page extraction complete.")
            
            # Format the company details for CSV
            #founders = "; ".join([f"{f['name']} ({f.get('Founder_linkedin_url', '')} {f.get('Founder_twitter_url', '')})" for f in company_details['Founders']])
            file.write(f"{company_details['Name']},{company_details['Status']},{company_details['Batch']},{company_details['Team_size']},{company_details['Website']}\n")  # Save company details to the file


# Scrape by directory
if __name__ == "__main__":
    df = pd.read_csv('YC_URLs.csv')
    
    try:
        with open(f'yc_data/YC_Directory.csv', 'r', encoding='utf-8') as directory:
            last_completed_row = sum(1 for _ in directory) - 1
    except:
        last_completed_row = -1

    with open(f'yc_data/YC_Directory.csv', 'a', encoding='utf-8') as directory:
        if last_completed_row == -1:
            directory.write("Name,Status,Batch,Team_size,Website\n")

        for index, row in df.iterrows():
            if index < last_completed_row:
                continue

            batch = row['Batch']
            company_url = row['YC URL']

            count = f"({index + 1}/{len(df)})"
            print(f"{count} Extracting {company_url}...")
            
            company_yc_page = scrape_individual_yc_company_page(company_url=company_url)
            company_details = extract_company_details(company_yc_page)

            directory.write(f"{company_details['Name']},{company_details['Status']},{company_details['Batch']},{company_details['Team Size']},{company_details['Website']}\n")

# Get the company's current global google trends score, use the peak of ChatGPT, Facebook or YouTube as 100 points.
# Search the internet to get their current annual revenue/valuation?