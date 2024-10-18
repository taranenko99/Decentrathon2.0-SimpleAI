# Pydantic
from pydantic import BaseModel, Field


class CreateDoctor(BaseModel):
    telegram_id: int = Field(ge=0)
    individual_number: str = Field(min_length=12, max_length=12)


class CreatePatient(BaseModel):
    telegram_id: int = Field(ge=0)
    individual_number: str = Field(min_length=12, max_length=12)
    doctor_id: int = Field(ge=0)
