from datetime import datetime
from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    author: str
    content: str

class PostUpdate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    author: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True # SQLAlchemy 모델을 Pydantic 모델로 변환할 때 필요