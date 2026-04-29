from pydantic import BaseModel, Field
from typing import Optional



class Item(BaseModel):
    name: str
    price: float = Field(gt=0, description="必须大于0")
    description: Optional[str] = None

class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    age: Optional[int] = Field(gt=0, default=None)
    email: str
