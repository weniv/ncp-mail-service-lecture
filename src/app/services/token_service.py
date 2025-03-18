from datetime import timedelta
from src.app.core.redis_config import redis_client
from src.app.utils.auth import REFRESH_TOKEN_EXPIRE_DAYS

TOKEN_BLACKLIST_PREFIX = "blacklist:" # 토큰 블랙리스트 키 접두사
REFRESH_TOKEN_PREFIX = "refresh:"  # Refresh 토큰 저장 접두사
DEFAULT_TOKEN_EXPIRY = 60 * 30  # 토큰 유효 기간 (초)

class TokenService:
    """
    토큰을 블랙리스트에 추가합니다.
    expires_in: 블랙리스트에 보관할 시간(초) - 토큰 만료 시간과 일치해야 함
    """
    @classmethod
    def blacklist_token(cls, token: str, expires_in: int = DEFAULT_TOKEN_EXPIRY):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        redis_client.set(key, "1", ex=expires_in)
        return True
    
    """
    토큰이 블랙리스트에 있는지 확인합니다.
    """
    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        return redis_client.exists(key) == 1
    
    """
    모든 블랙리스트 토큰을 제거합니다. (테스트용)
    """
    @classmethod
    def clear_blacklist(cls):
        
        for key in redis_client.scan_iter(f"{TOKEN_BLACKLIST_PREFIX}*"):
            redis_client.delete(key)

    """
    사용자 ID와 연결된 refresh 토큰을 저장합니다.
    """
    @classmethod
    def store_refresh_token(cls, user_id: int, refresh_token: str):
        # 사용자별 refresh 토큰 키
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        
        # 토큰의 고유 식별자를 값으로 사용
        # 동일한 사용자의 이전 refresh 토큰도 유지 (멀티 디바이스 지원)
        redis_client.sadd(user_key, refresh_token)
        
        # Refresh 토큰 만료 시간 설정 (7일 + 여유 시간)
        redis_client.expire(user_key, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS + 1).total_seconds())
        
        return True
    
    """
    저장된 refresh 토큰이 유효한지 확인합니다.
    """
    @classmethod
    def validate_refresh_token(cls, user_id: int, refresh_token: str) -> bool:
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        return redis_client.sismember(user_key, refresh_token)
    
    """
    특정 refresh 토큰 또는 사용자의 모든 refresh 토큰을 무효화합니다.
    """
    @classmethod
    def revoke_refresh_token(cls, user_id: int, refresh_token: str = None):
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        
        # 특정 토큰만 삭제하거나 모든 토큰 삭제
        if refresh_token:
            redis_client.srem(user_key, refresh_token)
        else:
            redis_client.delete(user_key)
            
        return True