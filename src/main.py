from fastapi import Depends, FastAPI

from src.app.apis import post
from .app.apis import auth
from .app.database import Base, engine

from .app.schemas.user import UserCreate, UserResponse
from .app.services.user_service import UserService, get_user_service

app = FastAPI(
    title="FastAPI NCP Mailing Service",
    description="게시판과 NCP 메일 발송 기능을 제공하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(post.router, prefix="/posts", tags=["post"])

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



# 회원가입
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    created_user = user_service.create_user(user)

    return created_user