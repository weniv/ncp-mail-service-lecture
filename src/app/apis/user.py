from fastapi import APIRouter, Depends
from src.app.schemas.user import UserCreate, UserResponse
from src.app.services.user_service import UserService, get_user_service

router = APIRouter()

# 회원가입
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    created_user = user_service.create_user(user)

    return created_user