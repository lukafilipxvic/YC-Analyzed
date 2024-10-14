import pandas as pd

file_path = 'yc_data/YC_Directory.csv'
yc_data = pd.read_csv(file_path)

yc_data['Team Size'] = pd.to_numeric(yc_data['Team Size'], errors='coerce')
yc_data['Batch'] = yc_data['Batch'].str.strip()

status_distribution = yc_data['Status'].value_counts()

print(f'{status_distribution}')

team_size_by_status = yc_data.groupby('Status')['Team Size'].describe()

acquisition_data = yc_data[yc_data['Status'].isin(['Acquired', 'Public'])]
print(acquisition_data)