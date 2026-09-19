"""Routes package for the freelancer platform blueprints."""

from __future__ import annotations

from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.projects import projects_bp
from app.routes.freelancers import freelancers_bp
from app.routes.admin import admin_bp
from app.routes.api import api_bp


all_blueprints = (
    main_bp,
    auth_bp,
    projects_bp,
    freelancers_bp,
    admin_bp,
    api_bp,
)


__all__ = [
    "all_blueprints",
    "main_bp",
    "auth_bp",
    "projects_bp",
    "freelancers_bp",
    "admin_bp",
    "api_bp",
]
