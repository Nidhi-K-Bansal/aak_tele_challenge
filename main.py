from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from database import countries_collection
from models import CountryData
app = FastAPI()

@app.get("/", response_model=List[CountryData])
async def get_country_data(
    country_name: Optional[str] = Query(None, description="The name of the country to filter"),
    income_levels: Optional[str] = Query(None, description="The income levels to filter"),
    region: Optional[str] = Query(None, description="The region to filter"),
    skip: Optional[int] = Query(0, ge=0, description="Number of documents to skip"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Number of documents to return")
    ):
    try:
        query = {}
        if country_name:
            query["country_name"] = country_name
        if income_levels:
            query["income_levels"] = income_levels
        if region:
            query["region"] = region
        countries = await countries_collection.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(length=None)
        return [CountryData(**country) for country in countries]
    except Exception as e:
        return {'error': str(e)}

