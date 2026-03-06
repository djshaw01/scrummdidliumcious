"""Admin configuration routes — team management, completed-session deletion, and base URL.

Full implementation added in Phase 7 (US4 / T052).
"""

from flask import Blueprint

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
