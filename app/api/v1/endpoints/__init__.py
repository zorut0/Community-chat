from .user import router as user
from .messages import router as messages
from .auth import router as auth
from .community import router as community

__all__ = ['user', 'messages', 'auth', 'community']
