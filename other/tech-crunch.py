import stealth_requests as requests
import csv
from pydantic import BaseModel, HttpUrl, ValidationError, Field
from typing import Optional

class Company(BaseModel):
    name: str
    link: HttpUrl
    industry: str
    event: str
    image: Optional[HttpUrl] = Field(default=None)
    location: str
    money_raised: Optional[str] = Field(default=None)
    status: str

base_url = "https://techcrunch.com/wp-json/tc/v1/get-companies-data?pg="
total_pages = 75
csv_file = "techcrunch_disrupt_company_data.csv"

csv_headers = ["name", "link", "industry", "event", "image", "location", "money_raised", "status"]

def extract_data(company_json):
    """Extract and validate data using the Company model."""
    try:
        return Company(
            name=company_json.get("name"),
            link=company_json.get("link"),
            industry=company_json.get("industry"),
            event=company_json.get("event"),
            image=company_json.get("image"),
            location=company_json.get("location"),
            money_raised=company_json.get("money_raised"),
            status=company_json.get("status")
        )
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None

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
                    
                    validated_data = extract_data(company)
                    if validated_data:
                        writer.writerow(validated_data.model_dump())
        else:
            print(f"Failed to retrieve data from page {page} (status code {response.status_code})")

print(f"Data successfully validated and saved to {csv_file}")
