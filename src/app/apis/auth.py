from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.app.dependencies.auth import get_current_user
from src.app.models.user import User
from src.app.schemas.auth import Token, LoginRequest
from src.app.services.auth_service import AuthService, get_auth_service
from src.app.services.token_service import TokenService
from src.app.utils.auth import get_token_expiry

router = APIRouter()

"""
사용자 로그인 및 JWT 토큰 발급
"""
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    사용자 로그인 및 JWT 토큰 발급
    """
    # 사용자 인증
    user = auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="인증 실패",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 토큰 생성
    token_data = auth_service.create_user_token(user)
    
    return token_data

# OAuth2 호환 로그인 엔드포인트 (Swagger UI에서 인증 가능)
"""
OAuth2 호환 토큰 발급 (form 데이터 사용)
"""
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service) 
):
    # OAuth2 폼 데이터를 LoginRequest로 변환
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password
    )
    
    # 사용자 인증
    user = auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="인증 실패",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 토큰 생성
    token_data = auth_service.create_user_token(user)
    
    return token_data

"""
사용자 로그아웃 - 현재 토큰을 블랙리스트에 추가
"""
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # 현재 토큰의 만료 시간 계산
    token_expiry = get_token_expiry(current_user.token)
    
    # 토큰을 블랙리스트에 추가
    TokenService.blacklist_token(current_user.token, token_expiry)
    
    return {"message": "로그아웃되었습니다."}