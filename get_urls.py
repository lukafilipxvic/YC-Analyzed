from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def get_all_urls(batch_code: str):
    url = f'https://www.ycombinator.com/companies?batch={batch_code}'

    # Initialize the WebDriver
    driver = webdriver.Chrome()  # or use webdriver.Firefox() for Firefox
    driver.get(url)
    
    time.sleep(1)

    # Scroll to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Scrape all URLs from the page
    links = driver.find_elements(By.TAG_NAME, "a")
    urls = [link.get_attribute("href") for link in links if link.get_attribute("href") is not None]
    urls = [url for url in urls if "/companies/" in url and "/companies/founders" not in url]
    driver.quit()
    return urls

if __name__ == "__main__":
    # Using the YC batches CSV file with pandas.   
    print(get_all_urls(batch_code="S24"))
    #df = pd.read_csv('YC_batches.csv')

    # Loop through each row in the DataFrame
    #for index, row in df.iterrows():
    #    batch = row['Batch']
    #    print(get_all_urls(batch_code=batch))