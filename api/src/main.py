from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
from enum import Enum
from pydantic_settings import BaseSettings

# Configuration class for environment-specific settings
class Settings(BaseSettings):
    # API settings
    api_title: str = "YC Vault API"
    api_description: str = "API for accessing Y Combinator startup data"
    api_version: str = "0.1.0"
    
    # Data settings
    # If DATA_DIR is set as an environment variable, use that (for local development)
    # Otherwise, default to a path relative to the current file (for Docker)
    data_dir: str = os.getenv(
        "DATA_DIR", 
        str(Path(__file__).resolve().parent.parent.parent.parent / "data")
    )
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        print(f"Using data directory: {self.data_dir}")

# Load settings
settings = Settings()

# Create custom JSON response class with pretty printing
class PrettyJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=True,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    default_response_class=PrettyJSONResponse
)

# Create a main v1 router
v1_router = APIRouter(prefix="/v1")

# Create a router for dataset endpoints
datasets_router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Create a new router for companies and founders
data_router = APIRouter(tags=["Data"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure base path for data
DATA_DIR = Path(settings.data_dir)

# Define possible status options based on the model
class CompanyStatus(str, Enum):
    ACTIVE = "Active"
    ACQUIRED = "Acquired"
    INACTIVE = "Inactive"
    PUBLIC = "Public"


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description
    }


def find_nearest_dataset(target_date: str = None) -> str:
    """Find the nearest dataset date to the provided date or use the latest dataset"""
    if not target_date:
        # Use current date if not provided
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    # Check if date format is valid
    if target_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', target_date):
        # Invalid format, use the latest dataset
        formatted_date = None
    else:
        formatted_date = target_date
    
    # Get all dataset directories
    datasets = []
    for item in DATA_DIR.iterdir():
        if item.is_dir() and re.match(r'^\d{4}-\d{2}-\d{2}$', item.name):
            datasets.append(item.name)
    
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found")
    
    # Sort datasets by date
    datasets = sorted(datasets, reverse=True)
    
    if not formatted_date:
        # Return the latest dataset
        return datasets[0]
    
    # Find the nearest dataset date
    if formatted_date in datasets:
        return formatted_date
    
    # If exact match not found, find the nearest earlier date
    earlier_datasets = [d for d in datasets if d <= formatted_date]
    if earlier_datasets:
        return earlier_datasets[0]
    
    # If no earlier date, use the oldest dataset
    return datasets[-1]


@datasets_router.get("/datasets", response_model=List[str])
async def list_datasets():
    """List all available dataset dates"""
    # Get all subdirectories in the data directory that are dates (YYYY-MM-DD format)
    datasets = []
    
    for item in DATA_DIR.iterdir():
        if item.is_dir() and item.name not in ['archived']:
            try:
                # Check if directory name follows date format
                if item.name[0].isdigit():
                    datasets.append(item.name)
            except (ValueError, IndexError):
                pass
    
    return sorted(datasets, reverse=True)


@datasets_router.get("/datasets/{dataset_date}")
async def get_dataset_files(dataset_date: str):
    """Get available files for a specific dataset date"""
    dataset_dir = DATA_DIR / dataset_date
    
    if not dataset_dir.exists() or not dataset_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Dataset for {dataset_date} not found")
    
    files = []
    for file in dataset_dir.iterdir():
        if file.is_file():
            # Get file extension without the dot
            ext = file.suffix[1:] if file.suffix else ""
            files.append({
                "filename": file.name,
                "size_bytes": file.stat().st_size,
                "extension": ext
            })
    
    return {"dataset": dataset_date, "files": files}


@datasets_router.get("/datasets/{dataset_date}/{file_name}")
async def get_dataset_data(
    dataset_date: str, 
    file_name: str,
    limit: Optional[int] = Query(None, description="Limit the number of records returned"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Get data from a specific file in a dataset"""
    file_path = DATA_DIR / dataset_date / file_name
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {file_name} not found in dataset {dataset_date}")
    
    try:
        # Handle different file formats
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
            
            # Get total records
            total_records = len(df)
            
            # Apply pagination if specified
            if limit is not None:
                df = df.iloc[offset:offset+limit]
            
            return {
                "dataset": dataset_date,
                "file": file_name,
                "total_records": total_records,
                "limit": limit,
                "offset": offset,
                "data": df.to_dict(orient="records")
            }
        
        elif file_name.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Excel files cannot be streamed directly via API. Please convert to CSV.")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_name}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")


def handle_nan(value: Any) -> Any:
    """Convert NaN values to None for JSON serialization"""
    if pd.isna(value) or (isinstance(value, float) and np.isnan(value)):
        return None
    return value


@data_router.get("/companies")
async def get_companies(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    batch: Optional[str] = Query(None, description="YC batch (e.g., W21, S22)"),
    status: Optional[CompanyStatus] = Query(None, description="Company status (Active, Acquired, Inactive, Public)"),
    industry: Optional[str] = Query(None, description="Industry category"),
    city: Optional[str] = Query(None, description="Company's city location"),
    team_size: Optional[int] = Query(None, description="Team size"),
    limit: Optional[int] = Query(None, description="Limit the number of records returned"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """
    Get YC companies with filtering options
    
    This endpoint returns YC companies from the dataset closest to the provided date.
    You can filter companies by batch, status, industry, city, and team size.
    """
    # Find the nearest dataset to the requested date
    dataset_date = find_nearest_dataset(date)
    
    # Create message when date is different than requested
    date_message = None
    if date and date != dataset_date:
        date_message = f"Requested date {date} not found. Using nearest available date: {dataset_date}"
    
    # Construct the path to the companies CSV file
    companies_file = DATA_DIR / dataset_date / "YC_Companies.csv"
    
    if not companies_file.exists():
        raise HTTPException(status_code=404, detail=f"Companies data not found in dataset {dataset_date}")
    
    try:
        # Read the companies data
        df = pd.read_csv(companies_file)
        
        # Apply filters
        if batch:
            df = df[df['Batch'].str.lower() == batch.lower()]
        
        if status:
            df = df[df['Status'] == status.value]
        
        if industry and 'Industry' in df.columns:
            # Industry might be a comma-separated list, so we search within it
            df = df[df['Industry'].str.contains(industry, case=False, na=False)]
        
        # Check for city in Location column or City column if it exists
        if city:
            if 'City' in df.columns:
                df = df[df['City'].str.contains(city, case=False, na=False)]
            elif 'Location' in df.columns:
                df = df[df['Location'].str.contains(city, case=False, na=False)]
        
        if team_size is not None:
            if 'Team Size' in df.columns:
                df = df[df['Team Size'] == team_size]
            elif 'Team_Size' in df.columns:
                df = df[df['Team_Size'] == team_size]
            elif 'team_size' in df.columns:
                df = df[df['team_size'] == team_size]
        
        # Get total records after filtering
        total_records = len(df)
        
        # Apply pagination
        if limit is not None:
            df = df.iloc[offset:offset+limit]
        else:
            df = df.iloc[offset:]
        
        # Try to convert data to match YC_Company schema
        data = []
        for _, row in df.iterrows():
            company_data = {
                "name": row.get("Name", ""),
                "batch": row.get("Batch", ""),
                "status": row.get("Status", ""),
                "industry": handle_nan(row.get("Industry")),
                "team_size": handle_nan(row.get("Team Size")),
                "city": handle_nan(row.get("Location"))  # Using Location as city if no City column
            }
            data.append(company_data)
        
        return {
            "dataset": dataset_date,
            "date_message": date_message,
            "total_records": total_records,
            "limit": limit,
            "offset": offset,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing companies data: {str(e)}")


@data_router.get("/founders")
async def get_founders(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    batch: Optional[str] = Query(None, description="YC batch (e.g., W21, S22)"),
    status: Optional[CompanyStatus] = Query(None, description="Company status (Active, Acquired, Inactive, Public)"),
    industry: Optional[str] = Query(None, description="Industry category"),
    city: Optional[str] = Query(None, description="Company's city location"),
    first_name: Optional[str] = Query(None, description="Founder's first name"),
    last_name: Optional[str] = Query(None, description="Founder's last name"),
    limit: Optional[int] = Query(None, description="Limit the number of records returned"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """
    Get YC founders with filtering options
    
    This endpoint returns YC founders from the dataset closest to the provided date.
    You can filter founders by their company's batch, status, industry, city, and founder's name.
    """
    # Find the nearest dataset to the requested date
    dataset_date = find_nearest_dataset(date)
    
    # Create message when date is different than requested
    date_message = None
    if date and date != dataset_date:
        date_message = f"Requested date {date} not found. Using nearest available date: {dataset_date}"
    
    # Construct the path to the founders CSV file
    founders_file = DATA_DIR / dataset_date / "YC_Founders.csv"
    
    if not founders_file.exists():
        raise HTTPException(status_code=404, detail=f"Founders data not found in dataset {dataset_date}")
    
    try:
        # Read the founders data
        df = pd.read_csv(founders_file)
        
        # Apply filters
        if batch:
            df = df[df['Batch'].str.lower() == batch.lower()]
        
        if status:
            df = df[df['Status'] == status.value]
        
        if industry and 'Industry' in df.columns:
            # Industry might be a comma-separated list, so we search within it
            df = df[df['Industry'].str.contains(industry, case=False, na=False)]
        
        # Check for city in Location column or City column if it exists
        if city:
            if 'City' in df.columns:
                df = df[df['City'].str.contains(city, case=False, na=False)]
            elif 'Location' in df.columns:
                df = df[df['Location'].str.contains(city, case=False, na=False)]
        
        if first_name and "Founder's First Name" in df.columns:
            df = df[df["Founder's First Name"].str.contains(first_name, case=False, na=False)]
        
        if last_name and "Founder's Last Name" in df.columns:
            df = df[df["Founder's Last Name"].str.contains(last_name, case=False, na=False)]
        
        # Group founders by first and last name to handle multiple companies per founder
        founders = {}
        for _, row in df.iterrows():
            # Convert row to dict and handle all NaN values
            row_dict = row.to_dict()
            for k, v in row_dict.items():
                row_dict[k] = handle_nan(v)
            
            first = row_dict.get("Founder's First Name", "")
            last = row_dict.get("Founder's Last Name", "")
            founder_key = f"{first}_{last}"
            
            if founder_key not in founders:
                founders[founder_key] = {
                    "first_name": first,
                    "last_name": last,
                    "company_count": 1,
                    "founder_linkedin_url": row_dict.get("Founder's LinkedIn"),
                    "founder_twitter_url": row_dict.get("Founder's Twitter"),
                    "companies": []
                }
            else:
                founders[founder_key]["company_count"] += 1
            
            founders[founder_key]["companies"].append({
                "name": row_dict.get("Name", ""),
                "batch": row_dict.get("Batch", ""),
                "status": row_dict.get("Status", ""),
                "industry": row_dict.get("Industry"),
                "team_size": row_dict.get("Team Size"),
                "city": row_dict.get("Location")
            })
        
        # Convert to list and apply pagination
        data = list(founders.values())
        total_records = len(data)
        
        # Apply pagination
        if limit is not None:
            data = data[offset:offset+limit]
        else:
            data = data[offset:]
        
        return {
            "dataset": dataset_date,
            "date_message": date_message,
            "total_records": total_records,
            "limit": limit,
            "offset": offset,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing founders data: {str(e)}")


# Include both routers in the main app
v1_router.include_router(data_router)
v1_router.include_router(datasets_router)
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 