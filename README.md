# YC Vault
 Analysis on every YC Batch ever.
 Read the initial blog post [here.](https://lukafilipovic.com/writing/2024/10/12/analysing-every-y-combinator-batch-ever/)

 ## Why?
Exceptional founders deliver exceptional results. Y Combinator has one of the highest concentrations of technical founders.
Companies like Airbnb, Docker, Instacart and Coinbase were all brought up through the accelerator. But they only represent the top percentile. 
That's why I built YC Vault.

## Requirements
Any language model of your choice through LiteLLM. High-performing models like GPT-4o-mini are recommended for their data extraction accuracy.

## Project installation
```
git clone https://github.com/lukafilipxvic/YC-Vault.git
```
```
uv sync
```

1. Set up the ```.env``` file with your OpenAI API key.
2. Type all the batch IDs into YC_Batches.csv. This file will require updating as new batches are founded. 
3. Run ```run_pipeline.py``` to perform the scape.

## Time to Complate
```get_yc_urls.py``` takes 5.3 minutes to scrape all YC URLs.

```get_yc_data.py``` takes 4.6 seconds to run for one company, taking 6.3 hours to scrape 5,000 YC companies synchronously.

## Cost to Scrape
```get_yc_data.py``` with GPT-4o-mini costs ≈ $0.00111 per YC company page, costing approximately $5.56 to scrape 5,000 YC companies.

In comparison, Gumloop charges 5 tokens to use a web-scraper and GPT-4o-mini twice, costing $80.83 to scrape 5,000 YC companies.

The project is 14.5x cheaper then Gumloop...