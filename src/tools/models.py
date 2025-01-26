from typing import Optional, Literal, List
from pydantic import BaseModel, ValidationError, AfterValidator, Field, HttpUrl
from typing import Annotated

def exclude_commas(text: Optional[str]) -> str:
    if text is None:
        return text
    elif "," in text:
        raise ValueError("Variable must not commain commas.")
    return text

class Company_Path(BaseModel):
    company_path: List[str] = Field(..., description="Company path.", examples=["coinbase", "instacart"])

class Founder(BaseModel):
    first_name: Annotated[str, AfterValidator(exclude_commas), Field(description="Founder's first name only. No Nicknames.")]
    last_name: Annotated[str, AfterValidator(exclude_commas), Field(description="Founder's last name.")]
    founder_linkedin_url: Optional[HttpUrl] = Field(description="Founder's LinkedIn Profile URL.", default=None)
    founder_twitter_url: Optional[HttpUrl] = Field(description="Founder's Twitter Profile URL.", default=None)

class YC_Company(BaseModel):
    name: str = Field(description="Name of the company.")
    batch: str = Field(description="YC batch code of participation. W for winter, S for summer, F for fall from F24, X for spring from X25.")
    status: Literal["Active", "Inactive", "Acquired", "Public"] = Field(description="Status of the company.")
    industry: Optional[str] = Field(description="Industry tags of the company.")
    team_size: Optional[int] = Field(description="Team size.")
    city: Annotated[Optional[str], AfterValidator(exclude_commas), Field(description="Name of the company's HQ city only.", default=None)]
    founders: Optional[List[Founder]] = Field(default=None)

if __name__ == "__main__":
    try:
        company = YC_Company(
            name="Coinbase",
            batch="W09",
            status='Active',
            industry='"marketplace AI"',
            team_size=100,
            city="London",
            founders=[Founder(first_name="Brian, not", last_name="Armstrong")])
    except ValidationError as e:
        print(e)