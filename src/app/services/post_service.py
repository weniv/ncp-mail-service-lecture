from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

class PostService:
    def __init__(self, db: Session):
        self.db = db

    async def create_post(self, post: PostCreate):
        created_post = Post(**post.model_dump())

        self.db.add(created_post)
        self.db.commit()
        self.db.refresh(created_post)

        return created_post

    async def get_posts(self):
        """방법1"""
        query = (
            select(Post).
            order_by(Post.created_at.desc())
        )
        posts = self.db.execute(query).scalars().all()
        """방법2(sqlalchemy 2.0에서 deprecated)"""
        # posts = db.query(Post).order_by(Post.created_at.desc()).all()

        return posts
    
    async def get_post(self, post_id: int):
        """방법1"""
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()
        """방법2(sqlalchemy 2.0에서 deprecated)"""
        # post = db.query(Post).filter(Post.id == post_id).first()

        return post
    
    async def update_post(self, post_id: int, post_update: PostUpdate):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
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
    
    async def delete_post(self, post_id: int):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return False

        self.db.delete(post)
        self.db.commit()

        return True
    
def get_post_service(db: Session = Depends(get_db)):
    return PostService(db)