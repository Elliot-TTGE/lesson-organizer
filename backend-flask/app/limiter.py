import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def get_rate_limit_key():
    """
    Returns user ID for authenticated requests, IP for unauthenticated.
    Falls back gracefully when JWT is missing/invalid.
    """
    try:
        # Attempt to verify JWT in request (doesn't require @jwt_required)
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        
        if user_id is not None:
            return f"user:{user_id}"
        else:
            return f"ip:{get_remote_address()}"
    except Exception:
        # JWT invalid/expired/missing - fall back to IP
        return f"ip:{get_remote_address()}"

# Initialize the limiter without default limits
# Rate limits will only apply to routes with explicit @limiter.limit() decorators
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=os.getenv("REDIS_URL"),
    strategy="fixed-window",
    headers_enabled=True
)
