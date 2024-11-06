import stealth_requests as requests
import csv
from litellm import completion
from pydantic import BaseModel, HttpUrl, ValidationError, Field
from typing import Optional
import instructor

class Company(BaseModel):
    name: str
    link: HttpUrl
    industry: str
    event: str
    image: HttpUrl
    location: str
    money_raised: Optional[int] = Field(default=None)
    status: str

client = instructor.from_litellm(completion)

base_url = "https://techcrunch.com/wp-json/tc/v1/get-companies-data?pg="
total_pages = 75
csv_file = "validated_companies_data.csv"

csv_headers = ["name", "link", "industry", "event", "image", "location", "money_raised", "status"]

def extract_data(json_data):
    response = client.chat.completions.create(
        model="groq/llama-3.1-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"Extract the name, link, industry, event, image, location, money_raised, status from the provided json into the model 'Company'.",
            },
            {
                "role": "user",
                "content": f"{json_data}",
            }
        ],
        response_model=Company,
    )
    return response

with open(csv_file, mode="w", newline='', encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    
    total_companies = 0

    for page in range(1, total_pages + 1):
        print(f"Processing page {page}...")
        url = f"{base_url}{page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "companies" in data.get("data", {}):
                companies = data["data"]["companies"]
                
                for company in companies:
                    total_companies += 1
                    print(f"Processing Company #{total_companies}...")
                    try:
                        validated_data = extract_data(company)
                        #print(validated_data.model_dump_json(indent=2))
                        writer.writerow(validated_data.model_dump())
                    except ValidationError as e:
                        print(f"Validation error: {e}")
                    except Exception as e:
                        print(f"Error processing data for page {page}: {e}")
        else:
            print(f"Failed to retrieve data from page {page} (status code {response.status_code})")

print(f"Data successfully validated and saved to {csv_file}")
