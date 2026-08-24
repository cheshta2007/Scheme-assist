from pydantic import BaseModel, Field
from typing import List, Optional


class UserProfile(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Age of the user in years")
    income: float = Field(..., ge=0.0, description="Annual income of the user")
    state: str = Field(..., description="State of residence")
    occupation: str = Field(..., description="Occupation of the user")
    category: str = Field(..., description="Social category (e.g. General, OBC, SC, ST)")
    gender: str = Field(..., description="Gender (e.g. Male, Female, Other)")


class SchemeResult(BaseModel):
    scheme: str
    eligible: bool
    failed_on: List[str]
    required_documents: List[str]
    official_source: str
    application_link: str
    explanation: Optional[str] = None
