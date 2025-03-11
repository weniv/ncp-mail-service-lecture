# app/services/auth_service.py
from datetime import timedelta
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.models.user import User
from src.app.schemas.auth import LoginRequest
from src.app.utils.security import verify_password
from src.app.utils.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    """
    사용자 인증을 수행합니다.
    """
    def authenticate_user(self, login_data: LoginRequest):
        # 사용자 조회
        query = (
            select(User).
            where(User.username == login_data.username)
        )
        user = self.db.execute(query).scalar_one_or_none()
        
        # 사용자가 존재하지 않거나 비밀번호가 일치하지 않는 경우
        if not user or not verify_password(login_data.password, user.password):
            return None
    
        return user
    
    """
    사용자 정보를 기반으로 액세스 토큰을 생성합니다.
    """
    def create_user_token(self, user: User):
        # 토큰에 포함될 데이터
        token_data = {
            "sub": user.username,
            "email": user.email,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
        
        # 만료 시간 설정
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 액세스 토큰 생성
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)