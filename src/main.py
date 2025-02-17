from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from app.database import Base, engine, get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from sqlalchemy.orm import Session

app = FastAPI(
    title="FastAPI NCP Mailing Service",
    description="게시판과 NCP 메일 발송 기능을 제공하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/ping")
async def ping_db():
    try:
        with engine.connect() as conn:
            return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

# 게시글 생성
@app.post(
        "/posts/", 
        response_model=PostResponse,
        summary="새 게시글 작성",
        description="새로운 게시글을 생성합니다.",
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    created_post = Post(**post.model_dump())

    db.add(created_post)
    db.commit()
    db.refresh(created_post)

    return created_post

# 전체 게시글 목록 조회
@app.get(
        "/posts/",
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
def get_posts(db: Session = Depends(get_db)):
    """방법1"""
    query = (
        select(Post).
        order_by(Post.created_at.desc())
    )
    posts = db.execute(query).scalars().all()
    """방법2(sqlalchemy 2.0에서 deprecated)"""
    # posts = db.query(Post).order_by(Post.created_at.desc()).all()

    if posts is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return posts

# 특정 게시글 조회
@app.get(
        "/posts/{post_id}", 
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
def get_post(post_id: int, db: Session = Depends(get_db)):
    """방법1"""
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()
    """방법2(sqlalchemy 2.0에서 deprecated)"""
    # post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

# 게시글 수정
@app.put(
        "/posts/{post_id}", 
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
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 수정할 데이터 업데이트
    for key, value in post_update.model_dump().items():
        setattr(post, key, value)
    
    db.commit()
    db.refresh(post)
    return post

# 게시글 삭제
@app.delete(
        "/posts/{post_id}", 
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
def delete_post(post_id: int, db: Session = Depends(get_db)):
    query = (
        select(Post).
        where(Post.id == post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    db.delete(post)
    db.commit()
    return {"message": "게시글이 성공적으로 삭제되었습니다."}