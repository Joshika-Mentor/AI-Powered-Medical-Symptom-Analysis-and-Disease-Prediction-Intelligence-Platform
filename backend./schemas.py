"""Request schemas (validation + automatic API docs)."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PatientIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Asha Raman"])
    age: int = Field(..., ge=0, le=120, examples=[58])
    gender: Literal["Male", "Female"]
    blood_pressure: Literal["Low", "Normal", "High"]
    cholesterol: Literal["Low", "Normal", "High"]
    # optional BRFSS-style lifestyle indicators (missing -> population defaults)
    bmi: Optional[float] = Field(None, ge=10, le=80, examples=[29.4])
    smoking: Optional[Literal["never", "former", "current"]] = None
    physically_active: Optional[bool] = None
    heavy_drinker: Optional[bool] = None
    conditions: Optional[str] = Field(None, max_length=300)
    allergies: Optional[str] = Field(None, max_length=300)


class SymptomsIn(BaseModel):
    fever: bool = False
    cough: bool = False
    fatigue: bool = False
    difficulty_breathing: bool = False


class AssessIn(BaseModel):
    """One-shot request: create the patient and run the full pipeline."""
    patient: PatientIn
    symptoms: SymptomsIn
    red_flags: list[str] = []   # urgent symptoms, used ONLY by the rule-based emergency check


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class RegisterIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8, max_length=100)


class LoginIn(BaseModel):
    email: str
    password: str
