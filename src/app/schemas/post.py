from datetime import datetime
from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    author: str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: int
    title: str | None
    author: str
    content: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True # SQLAlchemy 모델을 Pydantic 모델로 변환할 때 필요