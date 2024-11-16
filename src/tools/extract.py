from .llm import llms
from .models import Company_Path, YC_Company

client = llms()

def extract_urls(input, model: str = "llama3.1-70b"):
    resp = client.chat.completions.create(
        model=model,
        response_model=Company_Path,
        messages=[
            {
                "role": "system",
                "content": "You are an advanced company name extractor from URLs. DO NOT extract google or diversity categories (companies/black-founders, /hispanic-latino-founders, women-founders etc.)."
            },
            {
                "role": "user",
                "content": f"URLs: {input}"
            }
        ],
    )
    return resp.model_dump()

def extract_company_details(input, model: str = "gpt-4o-mini"):
    resp = client.chat.completions.create(
        model=model, # Use gpt-4o-mini from OpenAI, llama3.1-70b from Cerebras or llama-3.1-70b-versatile from Groq
        response_model=YC_Company,
        max_retries=10,
        messages=[
            {
                "role": "system",
                "content": "You are an advanced company details extractor. You will extract the relevant company information without any additional context or commentary. You must not include any commas in your response."
            },
            {
                "role": "user",
                "content": f"{input}"
            }
        ],
    )
    return resp.model_dump()
