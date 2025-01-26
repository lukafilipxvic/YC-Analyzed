import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import argparse

from tools.web_driver import setup_driver, scroll_to_bottom

def get_all_urls(driver, batch_code: str):
    url = f'https://www.ycombinator.com/companies?batch={batch_code}'
    driver.get(url)
    try:
        scroll_to_bottom(driver, scroll_pause=0.6)

        # Scrape all URLs from the page
        links = driver.find_elements(By.TAG_NAME, "a")
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href") is not None]
        excluded_categories = ["founders", "black-founders", "hispanic-latino-founders", "women-founders"]
        urls = [url for url in urls if "/companies/" in url and not any(category in url for category in excluded_categories)]
        
        return urls
    except TimeoutException:
        print(f"Timeout while loading batch {batch_code}")
        return []
    except NoSuchElementException as e:
        print(f"Element not found error: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    batch_file_path = "data/YC_Batches.csv"

    if date:
        os.makedirs(f'data/{date}', exist_ok=True)
        url_file_path = f"data/{date}/YC_URLs.csv"
    else:
        url_file_path = "data/YC_URLs.csv"

    all_urls = []
    batch_count = []
    df = pd.read_csv(batch_file_path)

    driver = setup_driver()

    try:
        for index, row in df.iterrows():
            batch = row['Batch']
            count = row['Count']

            retries = 3
            batch_urls = []
            while retries > 0 and (len(batch_urls) == 0 or abs(len(batch_urls) - count) > 10):
                batch_urls = get_all_urls(driver, batch_code=batch)
                retries -= 1

            if not batch_urls:
                print(f"Failed to retrieve URLs for {batch} after multiple attempts.")
                continue

            if count != len(batch_urls):
                print(f'Scraped {len(batch_urls)} URLs for {batch} (expected {count}).')

            all_urls.extend([(batch, url) for url in batch_urls])
            batch_count.append((batch, len(batch_urls)))

        pd.DataFrame(all_urls, columns=['Batch', 'YC URL']).to_csv(url_file_path, index=False)
        print(f"Data saved to {url_file_path}")
        pd.DataFrame(batch_count, columns=['Batch', 'Count']).to_csv(batch_file_path, index=False)
        print(f"Batch count saved to {batch_file_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
