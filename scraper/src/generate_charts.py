import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

def setup_file_paths(date=None):
    if date:
        directory = f'data/{date}'
        directory_file_path = f"data/{date}/YC_Companies.csv"
    else:
        directory = 'data/'
        directory_file_path = "data/YC_Companies.csv"
    os.makedirs(directory, exist_ok=True)
    return directory_file_path

def main():
    parser = argparse.ArgumentParser(description="Fetch YC URLs with date.")
    parser.add_argument('--date', type=str, help="Current date in YYYY-MM-DD format")
    args = parser.parse_args()
    date = args.date

    file_path = setup_file_paths(date=date)
    data = pd.read_csv(file_path)

    # Set 'Batch' as a categorical type with the original order
    batches = data['Batch'].unique()  # Get unique batches in the order they appear
    data['Batch'] = pd.Categorical(data['Batch'], categories=batches, ordered=True)

    # YC Batch Size Over Time
    batches = data['Batch']
    batch_counts = Counter(batches)
    batch_names, counts = zip(*batch_counts.items())

    plt.figure(figsize=(12, 6))
    plt.bar(batch_names, counts, color='skyblue')
    plt.title('YC Batch Size Over Time', fontsize=16)
    plt.xlabel('Batch', fontsize=12)
    plt.ylabel('Number of Companies', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # Batches vs Status
    batch_status_counts = data.groupby(['Batch', 'Status']).size().unstack()
    batch_status_percentages = batch_status_counts.div(batch_status_counts.sum(axis=1), axis=0) * 100
    batch_status_percentages.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='viridis')

    plt.title('Batches vs Status (Percentage)', fontsize=16)
    plt.xlabel('Batch', fontsize=12)
    plt.ylabel('Percentage of Companies', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Status')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # % of Team Size by Status Over Time
    team_size_by_status = data.groupby(['Batch', 'Status'])['Team Size'].sum()
    team_size_by_status.plot(kind='bar', stacked=True, figsize=(12, 6))

    plt.title('% of Team Size by Status Over Time', fontsize=16)
    plt.xlabel('Batch', fontsize=12)
    plt.ylabel('Average Team Size', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Status')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # Most common company first letter by status
    data['First Letter'] = data['Name'].str[0]
    most_common_letter = data.groupby('Status')['First Letter'].apply(lambda x: x.mode()[0])
    most_common_letter.plot(kind='bar', figsize=(12, 6), color='purple')
    plt.title('Most Common Company First Letter by Status', fontsize=16)
    plt.xlabel('Status', fontsize=12)
    plt.ylabel('Most Common First Letter', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()