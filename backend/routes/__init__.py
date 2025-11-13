from .auth_routes import auth_bp
from .config_routes import config_bp
from .health_routes import health_bp
from .audit_routes import audit_bp
from .users_routes import users_bp

__all__ = ['auth_bp', 'config_bp', 'health_bp', 'audit_bp', 'users_bp']
