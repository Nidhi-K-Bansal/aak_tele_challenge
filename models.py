from pydantic import BaseModel, Field
from typing import Optional

# Model for Metadata
class Metadata(BaseModel):
    value: Optional[str] = None
    year: Optional[str] = None
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# Model for Country Data
class CountryData(BaseModel):
    country_name: str
    poverty_headcount_ratio: Optional[Metadata] = Field(None, alias='poverty_headcount_ratio_at_$2.15_a_day')
    life_expectancy_at_birth: Optional[Metadata] = None
    population: Optional[Metadata] = None
    population_growth: Optional[Metadata] = None
    net_migration: Optional[Metadata] = None
    human_capital_index: Optional[Metadata] = None
    gdp: Optional[Metadata] = None
    gdp_per_capita: Optional[Metadata] = None
    gdp_growth: Optional[Metadata] = None
    unemployment: Optional[Metadata] = None
    inflation: Optional[Metadata] = None
    personal_remittances: Optional[Metadata] = None
    co2_emissions: Optional[Metadata] = None
    forest_area: Optional[Metadata] = None
    access_to_electricity: Optional[Metadata] = None
    annual_freshwater_withdrawals: Optional[Metadata] = None
    electricity_production_from_renewable_sources: Optional[Metadata] = None
    people_using_safely_managed_sanitation_services: Optional[Metadata] = None
    intentional_homicides: Optional[Metadata] = None
    central_government_debt: Optional[Metadata] = None
    statistical_performance_indicators: Optional[Metadata] = None
    individuals_using_the_internet: Optional[Metadata] = None
    proportion_of_seats_held_by_women_in_national_parliaments: Optional[Metadata] = None
    foreign_direct_investment: Optional[Metadata] = None
    region: str
    income_levels: Optional[str] = None
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True