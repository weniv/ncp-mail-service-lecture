from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError

# 실제 배포시에는 환경 변수로 보관해야 합니다
SECRET_KEY = "1234567890abcdefghijklmnopqrstuvwxyz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""
JWT 액세스 토큰을 생성합니다.
"""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT 페이로드에 만료 시간 추가
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

"""
JWT 토큰을 검증하고 페이로드를 반환합니다.
"""
def verify_token(token: str) -> dict:
    try:
        # 토큰 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # 토큰이 유효하지 않을 경우 None 반환
        return None