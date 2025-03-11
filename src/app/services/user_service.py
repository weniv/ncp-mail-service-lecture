from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from src.app.database import get_db
from src.app.models.user import User
from src.app.schemas.user import UserCreate
from src.app.utils.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
            self.db = db
            
    def create_user(self, user: UserCreate):
        # 이메일 중복 확인
        db_user = self.get_user_by_email(user.email)
    
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="이미 존재하는 이메일입니다."
            )
            
        # 사용자명 중복 확인
        db_user = self.get_user_by_username(user.username)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="이미 존재하는 사용자 이름입니다."
            )
        
        # 새 사용자 생성
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_email(self, email: str):
        query = (
            select(User).
            where(User.email == email)
        )
        return self.db.execute(query).scalar_one_or_none()
    
    def get_user_by_username(self, username: str):
        query = (
            select(User).
            where(User.username == username)
        )
        return self.db.execute(query).scalar_one_or_none()
    
def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)