from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: List[str] = Field(min_length=1)
    style: str = "Modern"
    notes: Optional[str] = ""

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = "Birthday"
    venue: str = "Home"
    notes: Optional[str] = ""

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    planner: str
    budget: float
    summary: str
    budget_allocation: dict
    recommendations: list
