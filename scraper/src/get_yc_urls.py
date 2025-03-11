import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from tools.web_driver import setup_driver, scroll_to_bottom
import argparse
import concurrent.futures
import time
from tqdm import tqdm

def get_all_urls(batch_code):
    """Fetch all startup URLs for a given YC batch."""
    driver = setup_driver()
    try:
        url = f'https://www.ycombinator.com/companies?batch={batch_code}'
        driver.get(url)
        
        time.sleep(1)

        # Scroll to load all companies on the page
        scroll_to_bottom(driver, pause_before=0.4, pause_after=0.2)

        # Extract and filter URLs
        links = driver.find_elements(By.TAG_NAME, "a")
        excluded_categories = {"founders", "black-founders", "hispanic-latino-founders", "women-founders"}
        urls = [
            link.get_attribute("href")
            for link in links
            if link.get_attribute("href") and "/companies/" in link.get_attribute("href")
               and not any(category in link.get_attribute("href") for category in excluded_categories)
        ]

        return batch_code, urls
    except TimeoutException:
        print(f"Timeout while loading batch {batch_code}. Retrying...")
        # Simple retry logic
        time.sleep(2)
        try:
            # Second attempt
            driver.get(url)
            driver.wai
            scroll_to_bottom(driver, pause_before=0.3, pause_after=0.3)
            links = driver.find_elements(By.TAG_NAME, "a")
            urls = [link.get_attribute("href") for link in links
                    if link.get_attribute("href") and "/companies/" in link.get_attribute("href")
                    and not any(category in link.get_attribute("href") for category in excluded_categories)]
            return batch_code, urls
        except Exception:
            return batch_code, []
    except Exception as e:
        print(f"Error retrieving URLs for batch {batch_code}: {e}")
        return batch_code, []
    finally:
        driver.quit()

def main():
    """Main script to fetch and save YC company URLs."""
    batch_file_path = "../data/YC_Batches.csv"

    # Parse command-line argument for date (optional)
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    parser.add_argument('--workers', type=int, default=6, help="Number of parallel workers")
    args = parser.parse_args()
    date = args.date
    max_workers = args.workers

    # Define file paths
    output_dir = f"../data/{date}" if date else "../data"
    os.makedirs(output_dir, exist_ok=True)
    url_file_path = os.path.join(output_dir, "YC_URLs.csv")

    # Read batch information
    df_batches = pd.read_csv(batch_file_path)
    all_urls = []
    
    # Check for existing data to enable resumption
    try:
        existing_df = pd.read_csv(url_file_path)
        processed_batches = set(existing_df['Batch'].unique())
        print(f"Found {len(processed_batches)} already processed batches. Will skip these.")
        df_batches = df_batches[~df_batches['Batch'].isin(processed_batches)]
    except FileNotFoundError:
        print("No existing data found. Processing all batches.")
    
    if df_batches.empty:
        print("All batches already processed. Exiting.")
        return

    # Process batches in parallel
    batches = list(df_batches['Batch'])
    print(f"Processing {len(batches)} batches with {max_workers} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(get_all_urls, batches), total=len(batches), desc="Fetching batches"))
    
    # Process results
    for batch, urls in results:
        if not urls:
            print(f"No URLs found for batch {batch}.")
            continue
            
        expected_count = df_batches.loc[df_batches['Batch'] == batch, 'Count'].values[0]
        actual_count = len(urls)
        
        if abs(actual_count - expected_count) > 5:
            print(f"Warning: Mismatch in expected vs. actual URL counts for {batch} (Expected: {expected_count}, Found: {actual_count}).")
        
        # Append results
        all_urls.extend([(batch, url) for url in urls])
        df_batches.loc[df_batches['Batch'] == batch, 'Count'] = actual_count
    
    # Save new results to CSV
    new_df = pd.DataFrame(all_urls, columns=['Batch', 'YC URL'])
    
    # Merge with existing data if available
    try:
        existing_df = pd.read_csv(url_file_path)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates()
        combined_df.to_csv(url_file_path, index=False)
        print(f"Updated company URLs saved to {url_file_path} (total: {len(combined_df)}).")
    except FileNotFoundError:
        new_df.to_csv(url_file_path, index=False)
        print(f"Company URLs saved to {url_file_path} (total: {len(new_df)}).")
    
    # Update batch count and save
    df_batches.to_csv(batch_file_path, index=False)
    print(f"Batch counts updated in {batch_file_path}.")

if __name__ == "__main__":
    main()
