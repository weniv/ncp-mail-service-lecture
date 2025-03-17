from datetime import datetime, timedelta
import time
from typing import Optional
import uuid

from jose import jwt, JWTError

# 실제 배포시에는 환경 변수로 보관해야 합니다
SECRET_KEY = "1234567890abcdefghijklmnopqrstuvwxyz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

"""
JWT 액세스 토큰을 생성합니다.
"""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    # 만료 시간 설정(30분)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT 페이로드에 만료 시간 추가
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # 토큰 고유 ID 추가
    })
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

"""
JWT refresh 토큰을 생성합니다.
"""
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    
    # 만료 시간 설정(7일)
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # JWT 페이로드에 만료 시간과 고유 ID 추가
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),  # 토큰 고유 ID 추가
        "type": "refresh"  # 토큰 타입 명시
    })
    
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
    
"""
JWT 토큰의 남은 만료 시간을 초 단위로 계산
"""
def get_token_expiry(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        exp = payload.get("exp")
        
        if exp:
            # 현재 시간과 만료 시간의 차이 계산
            remaining = exp - time.time()
            # 최소 1초 이상 설정
            return max(int(remaining), 1)
    except:
        pass
    
    # 기본값 (30분)
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60