"""Route blueprint registry for the SCRUMMDidliumcious application."""

from app.routes.admin import admin_bp
from app.routes.home import home_bp
from app.routes.poker_api import poker_api_bp
from app.routes.poker_pages import poker_pages_bp

__all__ = ["admin_bp", "home_bp", "poker_api_bp", "poker_pages_bp"]
