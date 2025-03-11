from .models import Company_Path, YC_Company

def extract_urls(client, input, model: str = "openai/gpt-4o-mini"):
    data, resp = client.chat.completions.create_with_completion(
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

def extract_company_details(client, input, model: str = "openai/gpt-4o-mini"):
    resp = client.chat.completions.create(
        model=model,
        response_model=YC_Company,
        max_retries=10,
        messages=[
            {
                "role": "system",
                "content": "Extract the relevant company information without any additional commentary:"
            },
            {
                "role": "user",
                "content": f"{input}"
            }
        ],
    )
    return resp.model_dump()
