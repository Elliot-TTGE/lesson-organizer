from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the limiter without default limits
# Rate limits will only apply to routes with explicit @limiter.limit() decorators
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True
)
