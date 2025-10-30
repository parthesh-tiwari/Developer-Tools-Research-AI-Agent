from pydantic import  BaseModel
from typing import List, Dict, Optional, Any

# Structured op for LLM focusing on developer tools
class CompanyAnalysis(BaseModel):
     pricing_model : str
     description: str
     is_open_source: Optional[bool] = None
     api_available  : Optional[bool] = None
     tech_stack : List[str]
     language_support : List[str]
     integration_capabilities: List[str]

# company information that can be used
class CompanyInformation(BaseModel):
    name : str
    description: str
    website: str
    pricing_model : str
    api_available: Optional[bool] = None
    is_open_source: Optional[bool] = None
    tech_stack : List[str] = []
    integration_capabilities : List[str] = []
    competitors : List[str] = []
    language_support : List[str] = []
    developer_experience_rating : Optional[str] = None


# Result that will tools to be called
class CompanyResult(BaseModel):
    query: str
    extracted_tools : List[str]
    companies : List[str]
    search_results : List[str]
    analysis : Optional[str] = None
