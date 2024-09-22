from selenium import webdriver
import time

def get_yc_batches():
    url = f'https://www.ycombinator.com/companies'

    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.get(url)
    
    time.sleep(2)

    body_element = driver.find_element("tag name", "body")
    body_text = body_element.text  # Get the plain text content of the body. great for scraping web content.

    print(body_text)

    driver.quit()
    return body_text

if __name__ == "__main__":
    get_yc_batches()