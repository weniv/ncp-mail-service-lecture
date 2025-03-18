from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    """
    CORS 미들웨어 설정
    """
    # 허용할 오리진 목록
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )