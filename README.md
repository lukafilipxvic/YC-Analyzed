# YC Vault
 Analysis on every YC Batch ever.
 Read the initial blog post [here.](https://lukafilipovic.com/writing/2024/10/12/analysing-every-y-combinator-batch-ever/)

 ## Why?
Y Combinator is one of the largest startup accelerators in the world.
It has one of the highest concentrations of technical founders.
Companies like Airbnb, Docker, Instacart and Coinbase were all brought up through the accelerator. But they only represent the top percentile.  

YC Vault is my attempt to make sense of the entire Y Combinator directory.

## Requirements
Any language model of your choice through LiteLLM. High-performing models like GPT-4o-mini are recommended for their data extraction accuracy.

## Project installation
```
git clone https://github.com/lukafilipxvic/YC-Vault.git
```
```
uv sync
```

3. Set up environment:
   - Create a `.env` file with your OpenAI API key
   - Example `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. Configure your data sources:
   - Update the `YC_Batches.csv` file with all batch IDs
   - This file will need updating as new batches are launched
2. Run the pipeline:
```
uv run python run_pipeline.py
```

## Performance

### Time Requirements

- `get_yc_urls.py`: ~2.5 minutes to scrape all YC URLs
- `get_yc_data.py`: ~3.68 seconds per company (approximately 5.11 hours to scrape 5,000 YC companies synchronously)

### Cost Analysis

- Using GPT-4o-mini costs approximately $0.00026 to extract one YC company page
- Total cost for 5,000 YC companies: ~$1.30
- For comparison, Gumloop costs ~$80.83 for the same data (62.18x more expensive)

## Data Structure

The scraping pipeline generates several CSV files:
- `YC_Companies.csv`: Company profiles and metrics
- `YC_Founders.csv`: Founder information and backgrounds
- `YC_URLs.csv`: Source URLs for all scraped data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under [AGPL-3.0](https://choosealicense.com/licenses/agpl-3.0/)
