from fastapi import FastAPI

from .app.apis import post, user
from .app.core.middlewares.cors import setup_cors
from .app.core.middlewares.security import setup_security
from .app.core.redis_config import init_redis
from .app.apis import auth
from .app.database import Base, engine


app = FastAPI(
    title="FastAPI NCP Mailing Service",
    description="게시판과 NCP 메일 발송 기능을 제공하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 미들웨어 설정
setup_cors(app)
setup_security(app)

# Redis 초기화
init_redis(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(post.router, prefix="/posts", tags=["post"])
app.include_router(user.router, tags=["user"])

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



