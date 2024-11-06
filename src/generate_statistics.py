import os
import argparse
import pandas as pd

def setup_file_paths(date=None):
    if date:
        directory = f'data/{date}'
        directory_file_path = f"data/{date}/YC_Directory.csv"
    else:
        directory = 'data/'
        directory_file_path = "data/YC_Directory.csv"
    os.makedirs(directory, exist_ok=True)
    return directory_file_path

def main():
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    file_path = setup_file_paths(date=date)
    yc_data = pd.read_csv(file_path)

    yc_data['Team Size'] = pd.to_numeric(yc_data['Team Size'], errors='coerce')
    yc_data['Batch'] = yc_data['Batch'].str.strip()

    status_distribution = yc_data['Status'].value_counts()

    print(f'{status_distribution}')

    team_size_by_status = yc_data.groupby('Status')['Team Size'].describe()

    acquisition_data = yc_data[yc_data['Status'].isin(['Acquired', 'Public'])]
    return acquisition_data

if __name__ == "__main__":
    main()