import os
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from cerebras.cloud.sdk import Cerebras
from groq import Groq
import instructor


class Company_path(BaseModel):
    Company_path: List[str] = Field(..., description="Company path.", examples=["coinbase", "instacart"])

class Founder(BaseModel):
    name: str = Field(description="Founder's full name.")
    Founder_linkedin_url: Optional[str] = Field(description="Their Linkedin Profile URL.", default=None)
    Founder_twitter_url: Optional[str] = Field(description="Their Twitter Profile URL.", default=None)

class YC_Company(BaseModel):
    Name: str = Field(description="Name of the company: No commas ','")
    Status: Literal["Active", "Inactive", "Acquired", "Public"] = Field(description="Status of the company.")
    Batch: str = Field(description="YC batch code of participation.")
    Team_size: Optional[int] = Field(description="Team size.")
    #Tags: list[str] = Field(description="Tags of the company.")
    Website: Optional[str] = Field(description="Link to their website.", default=None)
    #Founders: List[Founder]

os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['CEREBRAS_API_KEY'] = os.getenv('CEREBRAS_API_KEY')

#client = instructor.from_groq(Groq(), mode=instructor.Mode.TOOLS)
client = instructor.from_cerebras(Cerebras())

def extract_urls(input):
    resp = client.chat.completions.create(
        model="llama3.1-8b",
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
        response_model=Company_path,
    )
    return resp.model_dump()

def extract_company_details(input):
    resp = client.chat.completions.create(
        model="llama3.1-8b", # Rotate between llama-3.1-70b-versatile, llama-3.2-11b-text-preview, llama3-70b-8192 or llama-3.2-90b-text-preview. Cerebeas: llama3.1-70b
        messages=[
            {
                "role": "system",
                "content": "You are an advanced company details extractor. You will extract the relevant company information without any additional context or commentary."
            },
            {
                "role": "user",
                "content": f"{input}"
            }
        ],
        response_model=YC_Company,
    )
    return resp.model_dump()

if __name__ == "__main__":
    input = ['https://www.ycombinator.com/companies/black-founders', 'https://www.ycombinator.com/companies/hispanic-latino-founders', 'https://www.ycombinator.com/companies/women-founders', 'https://www.ycombinator.com/companies/outerport', 'https://www.ycombinator.com/companies/dreamrp', 'https://www.ycombinator.com/companies/melty', 'https://www.ycombinator.com/companies/syntra', 'https://www.ycombinator.com/companies/pathpilot', 'https://www.ycombinator.com/companies/standard-data', 'https://www.ycombinator.com/companies/kairo-health', 'https://www.ycombinator.com/companies/midship', 'https://www.ycombinator.com/companies/soma-lab', 'https://www.ycombinator.com/companies/merlin-ai', 'https://www.ycombinator.com/companies/freestyle', 'https://www.ycombinator.com/companies/arva-ai', 'https://www.ycombinator.com/companies/affil-ai', 'https://www.ycombinator.com/companies/orgorg', 'https://www.ycombinator.com/companies/patched', 'https://www.ycombinator.com/companies/village-labs', 'https://www.ycombinator.com/companies/mica-ai', 'https://www.ycombinator.com/companies/formula-insight', 'https://www.ycombinator.com/companies/overlap', 'https://www.ycombinator.com/companies/capitol-ai', 'https://www.ycombinator.com/companies/kart-ai', 'https://www.ycombinator.com/companies/void', 'https://www.ycombinator.com/companies/anglera', 'https://www.ycombinator.com/companies/xtraffic', 'https://www.ycombinator.com/companies/felafax', 'https://www.ycombinator.com/companies/henry-2', 'https://www.ycombinator.com/companies/hey-revia', 'https://www.ycombinator.com/companies/ficra', 'https://www.ycombinator.com/companies/rowboat-labs', 'https://www.ycombinator.com/companies/pipeshift', 'https://www.ycombinator.com/companies/vera-health', 'https://www.ycombinator.com/companies/pharos', 'https://www.ycombinator.com/companies/et-al', 'https://www.ycombinator.com/companies/keet', 'https://www.ycombinator.com/companies/terra-2', 'https://www.ycombinator.com/companies/ai-sell', 'https://www.ycombinator.com/companies/diode-computers-inc', 'https://www.ycombinator.com/companies/surebright', 'https://www.ycombinator.com/companies/usul', 'https://www.ycombinator.com/companies/saldor', 'https://www.ycombinator.com/companies/bucket-robotics', 'https://www.ycombinator.com/companies/oway', 'https://www.ycombinator.com/companies/elayne', 'https://www.ycombinator.com/companies/blaze-2', 'https://www.ycombinator.com/companies/pap', 'https://www.ycombinator.com/companies/mindely', 'https://www.ycombinator.com/companies/tradeflow', 'https://www.ycombinator.com/companies/voker', 'https://www.ycombinator.com/companies/rastro', 'https://www.ycombinator.com/companies/quetzal', 'https://www.ycombinator.com/companies/weavel', 'https://www.ycombinator.com/companies/moreta', 'https://www.ycombinator.com/companies/focus-buddy', 'https://www.ycombinator.com/companies/simplifine', 'https://www.ycombinator.com/companies/sepal-ai', 'https://www.ycombinator.com/companies/assembly-hoa', 'https://www.ycombinator.com/companies/autarc', 'https://www.ycombinator.com/companies/omnidock', 'https://www.ycombinator.com/companies/polymet', 'https://www.ycombinator.com/companies/kontigo', 'https://www.ycombinator.com/companies/remo', 'https://www.ycombinator.com/companies/propaya', 'https://www.ycombinator.com/companies/vendra', 'https://www.ycombinator.com/companies/argil', 'https://www.ycombinator.com/companies/zeropath', 'https://www.ycombinator.com/companies/actionbase', 'https://www.ycombinator.com/companies/corpdaq', 'https://www.ycombinator.com/companies/lumen-orbit', 'https://www.ycombinator.com/companies/dataleap', 'https://www.ycombinator.com/companies/zimi', 'https://www.ycombinator.com/companies/thyme', 'https://www.ycombinator.com/companies/ionworks', 'https://www.ycombinator.com/companies/rescript', 'https://www.ycombinator.com/companies/zigma-by-nextui', 'https://www.ycombinator.com/companies/helium', 'https://www.ycombinator.com/companies/ai-2', 'https://www.ycombinator.com/companies/haystack-software', 'https://www.ycombinator.com/companies/finosu', 'https://www.ycombinator.com/companies/odo', 'https://www.ycombinator.com/companies/baseline-ai', 'https://www.ycombinator.com/companies/zephr', 'https://www.ycombinator.com/companies/winford-ai', 'https://www.ycombinator.com/companies/cartage', 'https://www.ycombinator.com/companies/paasa', 'https://www.ycombinator.com/companies/blast', 'https://www.ycombinator.com/companies/lilac-labs', 'https://www.ycombinator.com/companies/palmier', 'https://www.ycombinator.com/companies/simple-ai', 'https://www.ycombinator.com/companies/sensei', 'https://www.ycombinator.com/companies/guardian-rf', 'https://www.ycombinator.com/companies/laminar-ai', 'https://www.ycombinator.com/companies/cerulion', 'https://www.ycombinator.com/companies/presti-ai', 'https://www.ycombinator.com/companies/the-forecasting-company', 'https://www.ycombinator.com/companies/praxos', 'https://www.ycombinator.com/companies/exa-laboratories', 'https://www.ycombinator.com/companies/schemeflow', 'https://www.ycombinator.com/companies/brighterway', 'https://www.ycombinator.com/companies/mineflow', 'https://www.ycombinator.com/companies/soff', 'https://www.ycombinator.com/companies/parley', 'https://www.ycombinator.com/companies/intryc', 'https://www.ycombinator.com/companies/pinnacle', 'https://www.ycombinator.com/companies/ember-robotics', 'https://www.ycombinator.com/companies/thunder-compute', 'https://www.ycombinator.com/companies/zeit-ai', 'https://www.ycombinator.com/companies/remade', 'https://www.ycombinator.com/companies/distro', 'https://www.ycombinator.com/companies/modern-realty', 'https://www.ycombinator.com/coms', 'https://www.ycombinator.com/companies/tabular', 'https://www.ycombinator.com/companies/callback', 'https://www.ycombinator.com/companies/flyflow', 'https://www.ycombinator.com/companies/bayesline', 'https://www.ycombinator.com/companies/digitalcarbon', 'https://www.ycombinator.com/companies/random-labs', 'https://www.ycombinator.com/companies/unsloth-ai', 'https://www.ycombinator.com/companies/codes-health', 'https://www.ycombinator.com/companies/entangl', 'https://www.ycombinator.com/companies/claimsorted', 'https://www.ycombinator.com/companies/mdhub', 'https://www.ycombinator.com/companies/hamming-ai', 'https://www.ycombinator.com/companies/genie', 'https://www.ycombinator.com/companies/prohostai', 'https://www.ycombinator.com/companies/educato-ai', 'https://www.ycombinator.com/companies/spaceium-inc', 'https://www.ycombinator.com/companies/comfy-deploy', 'https://www.ycombinator.com/companies/synnax', 'https://www.ycombinator.com/companies/theseus', 'https://www.ycombinator.com/companies/saphira-ai', 'https://www.ycombinator.com/companies/glasskube', 'https://www.ycombinator.com/companies/mem0', 'https://www.ycombinator.com/companies/cheers-2', 'https://www.ycombinator.com/companies/ply-health', 'https://www.ycombinator.com/companies/superfilter', 'https://www.ycombinator.com/companies/superunit', 'https://www.ycombinator.com/companies/undermind', 'https://www.ycombinator.com/companies/domu-technology-inc', 'https://www.ycombinator.com/companies/apten', 'https://www.ycs', 'https://www.ycombinator.com/companies/tabular', 'https://www.ycombinator.com/companies/callback', 'https://www.ycombinator.com/companies/flyflow', 'https://www.ycombinator.com/companies/bayesline', 'https://www.ycombinator.com/companies/digitalcarbon', 'https://www.ycombinator.com/companies/random-labs', 'https://www.ycombinator.com/companies/unsloth-ai', 'https://www.ycombinator.com/companies/codes-health', 'https://www.ycombinator.com/companies/entangl', 'https://www.ycombinator.com/companies/claimsorted', 'https://www.ycombinator.com/companies/mdhub', 'https://www.ycombinator.com/companies/hamming-ai', 'https://www.ycombinator.com/companies/genie', 'https://www.ycombinator.com/companies/prohostai', 'https://www.ycombinator.com/companies/educato-ai', 'https://www.ycombinator.com/companies/spaceium-inc', 'https://www.ycombinator.com/companies/comfy-deploy', 'https://www.ycombinator.com/companies/synnax', 'https://www.ycombinator.com/companies/theseus', 'https://www.ycombinator.com/companies/saphira-ai', 'https://www.ycombinator.com/companies/glasskube', 'https://www.ycombinator.com/companies/mem0', 'https://www.ycombinator.com/companies/cheers-2', 'https://www.ycombinator.com/companies/ply-health', 'https://www.ycombinator.com/companies/superfilter', 'https://www.ycombinator.com/companies/superunit', 'https://www.ycombinator.com/companies/undermind', 'https://www.ycombinator.com/companies/domu-technology-inc', 'https://www.ycombinator.com/companies/apten', 'https://www.ycombinator.com/companies/spherecast', 'https://www.ycombinator.com/companies/miru-ml', 'https://www.ycombinator.com/companies/cardlift', 'https://www.ycombinator.com/companies/abel-police', 'https://www.ycombinator.com/companies/ultra', 'https://www.ycombinator.com/companies/angstrom-ai', 'https://www.ycombinator.com/companies/coval', 'https://www.ycombinator.com/companies/evolvere-biosciences', 'https://www.ycombinator.com/companies/spur', 'https://www.ycombinator.com/companies/ligo-biosciences', 'https://www.ycombinator.com/companies/acx', 'https://www.ycombinator.com/companies/cracked', 'https://www.ycombinator.com/companies/fuse-2', 'https://www.ycombinator.com/companies/central', 'https://www.ycombinator.com/companies/simplex', 'https://www.ycombinator.com/companies/poka-labs']
    response = extract_urls(input)
    print(response['Company_path'])
    print(len(response['Company_path']))