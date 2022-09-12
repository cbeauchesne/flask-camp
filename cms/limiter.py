from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20000 per day", "2000 per hour", "300 per minute", "10 per second"],
    storage_uri="memory://",
)
