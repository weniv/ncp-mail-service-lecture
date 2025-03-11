from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies.auth import get_current_user
from src.app.models.user import User
from src.app.schemas.post import PostCreate, PostResponse, PostUpdate
from src.app.services.post_service import PostService, get_post_service


router = APIRouter()

"""
게시글 생성
인증된 사용자만 접근 가능
"""
@router.post(
        "/", 
        response_model=PostResponse,
        summary="새 게시글 작성",
        description="새로운 게시글을 생성합니다.",
)
def create_post(
    post: PostCreate, 
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user)
):
    created_post = post_service.create_post(post, current_user)

    return created_post

"""
전체 게시글 목록 조회
모든 사용자 접근 가능
"""
@router.get(
        "/",
        response_model=List[PostResponse],
        summary="게시글 목록 조회",
        description="전체 게시글 목록을 최신순으로 조회합니다.",
        responses={
            404: {
                "description": "게시글 조회 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "게시글을 찾을 수 없습니다.",
                        }
                    }
                }
            }
        }
)
def get_posts(post_service: PostService = Depends(get_post_service)):
    posts = post_service.get_posts()

    if posts is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return posts

"""
특정 게시글 조회
모든 사용자 접근 가능
"""
@router.get(
        "/{post_id}", 
        response_model=PostResponse,
        summary="특정 게시글 조회",
        description="게시글 ID를 기반으로 특정 게시글을 조회합니다.",
        responses={
            404: {
                "description": "게시글 조회 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "게시글을 찾을 수 없습니다.",
                        }
                    }
                }
            }
        }
)
def get_post(post_id: int, post_service: PostService = Depends(get_post_service)):
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

"""
게시글 수정
인증된 사용자만 접근 가능
"""
@router.patch(
        "/{post_id}", 
        response_model=PostResponse,
        summary="게시글 수정",
        description="특정 게시글의 내용을 수정합니다.",
        responses={
            404: {
                "description": "게시글 수정 실패",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "게시글을 찾을 수 없습니다.",
                        }
                    }
                }
            }
        }
)
def update_post(
    post_id: int, 
    post_update: PostUpdate, 
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user)
):
    post = post_service.update_post(post_id, post_update, current_user)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return post

"""
게시글 삭제
인증된 사용자만 접근 가능
"""
@router.delete(
        "/{post_id}", 
        response_model=dict,
        summary="게시글 삭제",
        description="특정 게시글을 삭제합니다.",
        responses={
            200: {
                "description": "게시글 삭제 성공",
                "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글이 성공적으로 삭제되었습니다.",
                    }
                }
            },
        },
            404: {
                "description": "게시글 삭제 실패",
                "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글을 찾을 수 없습니다.",
                    }
                }
            },
        }
    }
)
def delete_post(
    post_id: int, 
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user)
):
    post = post_service.delete_post(post_id, current_user)

    if post is False:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return {"message": "게시글이 성공적으로 삭제되었습니다."}