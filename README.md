# YC Analyzed
 Analysis on every YC Batch ever.
 Read the initial [blog post here](https://lukafilipovic.com/writing/2024/10/12/analysing-every-y-combinator-batch-ever/)

## Scraping the data yourself...
```
git clone https://github.com/lukafilipxvic/YC-Analyzed.git
```
1. Delete or move ```yc_data/YC_Directory.csv``` and ```YC_URLs.csv```
2. Run ```1_get_urls.py``` to scrape all the URLs into YC_URLs.csv
3. Run ```2_get_yc_data.py``` to scrape the YC page into the YC_Directory.csv file (Cerebras or Groq API Key required).