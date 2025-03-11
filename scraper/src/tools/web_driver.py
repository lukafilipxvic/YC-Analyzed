from selenium import webdriver
import time

def setup_driver():
    '''
    Set up and return a configured WebDriver instance.
    '''
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable image loading
        "profile.managed_default_content_settings.plugins": 2  # Disable video loading
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scroll_to_bottom(driver, pause_before=0.4, pause_after=0.2):
    """Scroll to the bottom of the page with a pause, returning when fully loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        time.sleep(pause_before)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_after)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height