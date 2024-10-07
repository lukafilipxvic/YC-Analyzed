from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

def get_all_urls(batch_code: str):
    url = f'https://www.ycombinator.com/companies?batch={batch_code}'

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable image loading
        "profile.managed_default_content_settings.plugins": 2  # Disable video loading
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    time.sleep(1)

    # Scroll to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        time.sleep(0.4)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Scrape all URLs from the page
    links = driver.find_elements(By.TAG_NAME, "a")
    urls = [link.get_attribute("href") for link in links if link.get_attribute("href") is not None]
    excluded_categories = ["founders", "black-founders", "hispanic-latino-founders", "women-founders"]
    urls = [url for url in urls if "/companies/" in url and not any(category in url for category in excluded_categories)]
    driver.quit()
    return urls

if __name__ == "__main__":
    all_urls = []
    df = pd.read_csv('YC_Batches.csv')

    for index, row in df.iterrows():
        batch = row['Batch']
        count = row['Count']
        batch_urls = get_all_urls(batch_code=batch)
        if count != len(batch_urls):
            print(f'Scraped {len(batch_urls)} URLs, while {batch} has {count} companies.')
        all_urls.extend([(batch, url) for url in batch_urls])  # Add batch and URL pairs to the list
    pd.DataFrame(all_urls, columns=['Batch', 'YC URL']).to_csv('YC_URLs.csv', index=False)