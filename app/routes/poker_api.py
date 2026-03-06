"""SCRUM Poker REST API routes — session lifecycle, voting, and leadership endpoints.

Full implementation added in Phases 4–7 (US1–US4 / T020, T030, T045, T052).
"""

from flask import Blueprint

poker_api_bp = Blueprint("poker_api", __name__, url_prefix="/api/poker")
