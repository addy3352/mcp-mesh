
from pydantic import BaseModel, Field
from typing import Optional, List

class MealEntry(BaseModel):
    date: str
    meal: str
    description: Optional[str] = None
    calories: float = Field(ge=0)
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0

class DailySummaryRequest(BaseModel):
    date: str

class MealsQuery(BaseModel):
    date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
