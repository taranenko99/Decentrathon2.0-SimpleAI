# Pydantic
from pydantic import BaseModel, Field

# Python
from typing import Optional


class CreateDoctor(BaseModel):
    id: Optional[int] = None
    telegram_id: int = Field(ge=0)
    individual_number: str = Field(min_length=12, max_length=12)

    class Config:
        json_schema_extra = {
            "examples": [{
                "telegram_id": 8259013952,
                "individual_number": "012583758345"
            }]
        }


class ViewAllDoctors(BaseModel):
    response: list[CreateDoctor]


class CreatePatient(BaseModel):
    id: Optional[int] = None
    telegram_id: int = Field(ge=0)
    individual_number: str = Field(min_length=12, max_length=12)
    doctor_id: int = Field(ge=0)

    class Config:
        json_schema_extra = {
            "examples": [{
                "telegram_id": 8259013952,
                "individual_number": "012583758345",
                "doctor_id": 25
            }]
        }


class ViewAllPatients(BaseModel):
    response: list[CreatePatient]
