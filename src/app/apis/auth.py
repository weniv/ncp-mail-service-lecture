from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.app.dependencies.auth import get_current_user
from src.app.models.user import User
from src.app.schemas.auth import RefreshRequest, Token, LoginRequest
from src.app.services.auth_service import AuthService, get_auth_service
from src.app.services.token_service import TokenService
from src.app.utils.auth import get_token_expiry

router = APIRouter()

"""
사용자 로그인 및 JWT 토큰 발급
"""
@router.post(
        "/login", 
        response_model=Token,
        summary="사용자 로그인",
        description="사용자 로그인 후 JWT 토큰을 발급합니다.",
        responses={
            401: {
                "description": "인증 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "인증 실패",
                        }
                    }
                }
            }
        }
)
def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
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
@router.post(
        "/token", 
        response_model=Token,
        summary="OAuth2 호환 토큰 발급",
        description="OAuth2 호환 토큰을 발급합니다.",
        responses={
            401: {
                "description": "인증 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "인증 실패",
                        }
                    }
                }
            }
        }
)
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
@router.post(
        "/logout",
        summary="사용자 로그아웃",
        description="사용자 로그아웃",
        responses={
            200: {
                "description": "로그아웃 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "로그아웃되었습니다.",
                        }
                    }
                }
            }
        }
)
def logout(
    current_user: User = Depends(get_current_user),
    refresh_token: str = None,
    ):
    # 현재 토큰의 만료 시간 계산
    token_expiry = get_token_expiry(current_user.token)
    
    # 토큰을 블랙리스트에 추가
    TokenService.blacklist_token(current_user.token, token_expiry)

    # 리프레시 토큰이 들어올 경우 해당 토큰 무효화
    if refresh_token:
        TokenService.revoke_refresh_token(current_user.id, refresh_token)
    
    return {"message": "로그아웃되었습니다."}

"""
Refresh 토큰을 사용하여 새로운 액세스 토큰 발급
"""
@router.post(
        "/refresh", 
        response_model=Token,
        summary="리프레시 토큰으로 액세스 토큰 갱신",
        description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.",
        responses={
            401: {
                "description": "사용자 접근 권한 인증 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "사용자 접근이 유효하지 않습니다.",
                        }
                    }
                }
            }
        }
)
def refresh_token(refresh_data: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    # 리프레시 토큰으로 새 액세스 토큰 발급
    tokens = auth_service.refresh_access_token(refresh_data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=401,
            detail="사용자 접근이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # refresh_token 필드 추가 (기존 리프레시 토큰 유지)
    tokens["refresh_token"] = refresh_data.refresh_token
    
    return tokens

"""
사용자의 모든 세션 로그아웃 - 현재 토큰을 블랙리스트에 추가하고
모든 리프레시 토큰 무효화
"""
@router.post(
        "/logout-all",
        summary="모든 기기 로그아웃",
        description="사용자의 모든 기기에서 로그아웃합니다.",
        responses={
            200: {
                "description": "모든 기기로부터 로그아웃 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "모든 기기로부터 로그아웃되었습니다.",
                        }
                    }
                }
            }
        }
)
def logout_all_sessions(current_user: User = Depends(get_current_user)):

    # 현재 액세스 토큰 블랙리스트에 추가
    token_expiry = get_token_expiry(current_user.token)
    TokenService.blacklist_token(current_user.token, token_expiry)
    
    # 사용자의 모든 리프레시 토큰 무효화
    TokenService.revoke_refresh_token(current_user.id)
    
    return {"message": "모든 기기로부터 로그아웃되었습니다."}