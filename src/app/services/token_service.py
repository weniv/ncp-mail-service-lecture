from app.core.redis_config import redis_client

# 토큰 블랙리스트 키 접두사
TOKEN_BLACKLIST_PREFIX = "blacklist:"
# 토큰 유효 기간 (초)
DEFAULT_TOKEN_EXPIRY = 60 * 30  # 30분

class TokenService:
    @classmethod
    def blacklist_token(cls, token: str, expires_in: int = DEFAULT_TOKEN_EXPIRY):
        """
        토큰을 블랙리스트에 추가합니다.
        expires_in: 블랙리스트에 보관할 시간(초) - 토큰 만료 시간과 일치해야 함
        """
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        redis_client.set(key, "1", ex=expires_in)
        return True
    
    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        """
        토큰이 블랙리스트에 있는지 확인합니다.
        """
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        return redis_client.exists(key) == 1
    
    @classmethod
    def clear_blacklist(cls):
        """
        모든 블랙리스트 토큰을 제거합니다. (테스트용)
        """
        for key in redis_client.scan_iter(f"{TOKEN_BLACKLIST_PREFIX}*"):
            redis_client.delete(key)