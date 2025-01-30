import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tools.web_driver import setup_driver, scroll_to_bottom
import argparse

def get_all_urls(driver, batch_code):
    """Fetch all startup URLs for a given YC batch."""
    url = f'https://www.ycombinator.com/companies?batch={batch_code}'
    driver.get(url)
    try:
        # Scroll to load all companies on the page
        scroll_to_bottom(driver, scroll_pause=0.6)

        # Extract and filter URLs
        links = driver.find_elements(By.TAG_NAME, "a")
        excluded_categories = {"founders", "black-founders", "hispanic-latino-founders", "women-founders"}
        urls = [
            link.get_attribute("href")
            for link in links
            if link.get_attribute("href") and "/companies/" in link.get_attribute("href")
               and not any(category in link.get_attribute("href") for category in excluded_categories)
        ]

        return urls
    except TimeoutException:
        print(f"Timeout while loading batch {batch_code}. Skipping.")
        return []
    except Exception as e:
        print(f"Error retrieving URLs for batch {batch_code}: {e}")
        return []

def main():
    """Main script to fetch and save YC company URLs."""
    batch_file_path = "data/YC_Batches.csv"

    # Parse command-line argument for date (optional)
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    # Define file paths
    output_dir = f"data/{date}" if date else "data"
    os.makedirs(output_dir, exist_ok=True)
    url_file_path = os.path.join(output_dir, "YC_URLs.csv")

    # Read batch information
    df_batches = pd.read_csv(batch_file_path)
    all_urls = []

    # Set up Selenium driver
    driver = setup_driver()

    try:
        # Process each batch
        for _, row in df_batches.iterrows():
            batch = row['Batch']
            expected_count = row['Count']

            print(f"Fetching URLs for batch {batch}...")

            # Fetch URLs
            urls = get_all_urls(driver, batch_code=batch)
            actual_count = len(urls)

            if actual_count == 0:
                print(f"No URLs found for batch {batch}.")
                continue

            if abs(actual_count - expected_count) > 5:
                print(f"Warning: Mismatch in expected vs. actual URL counts for {batch} (Expected: {expected_count}, Found: {actual_count}).")

            # Append results
            all_urls.extend([(batch, url) for url in urls])
            df_batches.loc[df_batches['Batch'] == batch, 'Count'] = actual_count

        # Save results to CSV
        pd.DataFrame(all_urls, columns=['Batch', 'YC URL']).to_csv(url_file_path, index=False)
        print(f"Company URLs saved to {url_file_path}.")

        # Update batch count and save
        df_batches.to_csv(batch_file_path, index=False)
        print(f"Batch counts updated in {batch_file_path}.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
