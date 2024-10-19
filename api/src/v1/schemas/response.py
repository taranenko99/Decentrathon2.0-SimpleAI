# Pydantic
from pydantic import BaseModel, Field


class ResponseSchema(BaseModel):
    response: str = Field(...) 


class ErrorSchema(BaseModel):
    error: str = Field(...)


class ResponseChat(BaseModel):
    trigger: int = Field(...) 
    bot_message: str = Field(...)
