from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.models.post import Post
from src.app.models.user import User
from src.app.schemas.post import PostCreate, PostUpdate

class PostService:
    def __init__(self, db: Session):
        self.db = db
    """
    게시글 생성
    """
    def create_post(self, post: PostCreate, user: User):
        created_post = Post(**post.model_dump())

        self.db.add(created_post)
        self.db.commit()
        self.db.refresh(created_post)

        return created_post

    """
    전체 게시글 목록 조회
    """
    def get_posts(self):
        """방법1"""
        query = (
            select(Post).
            order_by(Post.created_at.desc())
        )
        posts = self.db.execute(query).scalars().all()
        """방법2(sqlalchemy 2.0에서 deprecated)"""
        # posts = db.query(Post).order_by(Post.created_at.desc()).all()

        return posts
    
    """
    특정 게시글 조회
    """
    def get_post(self, post_id: int):
        """방법1"""
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()
        """방법2(sqlalchemy 2.0에서 deprecated)"""
        # post = db.query(Post).filter(Post.id == post_id).first()

        return post
    
    """
    게시글 수정
    작성자만 수정 가능
    """
    def update_post(self, post_id: int, post_update: PostUpdate, user: User):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return None
        
        # 작성자 확인
        if post.author_id != user.id:
            return None
        
        update_dict = {
            key: value
            for key, value in post_update.model_dump().items()
            if value is not None
        }

        for key, value in update_dict.items():
            setattr(post, key, value)

        self.db.commit()
        self.db.refresh(post)

        return post
    
    """
    게시글 삭제
    작성자만 삭제 가능
    """
    def delete_post(self, post_id: int, user: User):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return False
        
        # 작성자 확인
        if post.author_id != user.id:
            return False

        self.db.delete(post)
        self.db.commit()

        return True
    
def get_post_service(db: Session = Depends(get_db)):
    return PostService(db)