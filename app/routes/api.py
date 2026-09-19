"""JSON API blueprint for the freelancer platform."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Category, FreelancerProfile, Project, Proposal, Review, Skill, User
from app.routes.auth import current_user, login_required


api_bp = Blueprint("api", __name__, url_prefix="/api")


# --------------------------------------------------------------------------- #
#  Serializers
# --------------------------------------------------------------------------- #

def user_to_dict(user: User, *, detailed: bool = False) -> dict:
    data = {
        "id": user.id,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "country": user.country,
        "rating": user.average_rating,
    }
    if detailed:
        data.update(
            {
                "email": user.email,
                "bio": user.bio,
                "created_at": user.created_at.isoformat(),
            }
        )
    return data


def project_to_dict(project: Project) -> dict:
    return {
        "id": project.id,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "budget_display": project.budget_display,
        "status": project.status,
        "experience_level": project.experience_level,
        "project_type": project.project_type,
        "is_featured": project.is_featured,
        "views": project.views,
        "proposal_count": project.proposal_count,
        "category": project.category.name if project.category else None,
        "skills": [s.name for s in project.skills],
        "client": user_to_dict(project.client),
        "created_at": project.created_at.isoformat(),
    }


def freelancer_to_dict(profile: FreelancerProfile) -> dict:
    return {
        "id": profile.user_id,
        "full_name": profile.user.full_name,
        "headline": profile.headline,
        "hourly_rate": float(profile.hourly_rate) if profile.hourly_rate else None,
        "experience_years": profile.experience_years,
        "availability": profile.availability,
        "success_rate": profile.success_rate,
        "total_earned": float(profile.total_earned),
        "skills": [s.name for s in profile.skills],
        "rating": profile.user.average_rating,
    }


def proposal_to_dict(proposal: Proposal) -> dict:
    return {
        "id": proposal.id,
        "bid_amount": float(proposal.bid_amount),
        "delivery_days": proposal.delivery_days,
        "status": proposal.status,
        "cover_letter": proposal.cover_letter,
        "project_id": proposal.project_id,
        "freelancer": user_to_dict(proposal.freelancer),
        "created_at": proposal.created_at.isoformat(),
    }


# --------------------------------------------------------------------------- #
#  Public endpoints
# --------------------------------------------------------------------------- #

@api_bp.route("/health")
def health():
    return jsonify(status="ok")


@api_bp.route("/projects")
def list_projects():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 12, type=int), 50)
    q = (request.args.get("q") or "").strip()

    query = Project.query.filter_by(status="open")
    if q:
        query = query.filter(
            or_(Project.title.ilike(f"%{q}%"), Project.description.ilike(f"%{q}%"))
        )

    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        items=[project_to_dict(p) for p in pagination.items],
        page=pagination.page,
        pages=pagination.pages,
        total=pagination.total,
    )


@api_bp.route("/projects/<slug>")
def project_detail(slug: str):
    project = Project.query.filter_by(slug=slug).first()
    if project is None:
        return jsonify(error="پروژه یافت نشد"), 404
    return jsonify(project_to_dict(project))


@api_bp.route("/freelancers")
def list_freelancers():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 12, type=int), 50)

    query = FreelancerProfile.query.join(User).filter(User.is_active.is_(True))
    pagination = query.order_by(FreelancerProfile.success_rate.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        items=[freelancer_to_dict(f) for f in pagination.items],
        page=pagination.page,
        pages=pagination.pages,
        total=pagination.total,
    )


@api_bp.route("/categories")
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify(
        items=[
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "icon": c.icon,
                "project_count": len(c.projects),
            }
            for c in categories
        ]
    )


@api_bp.route("/skills")
def list_skills():
    skills = Skill.query.order_by(Skill.name).all()
    return jsonify(items=[{"id": s.id, "name": s.name, "slug": s.slug} for s in skills])


@api_bp.route("/stats")
def stats():
    from sqlalchemy import func

    return jsonify(
        projects=db.session.query(func.count(Project.id)).scalar() or 0,
        open_projects=db.session.query(func.count(Project.id))
        .filter(Project.status == "open")
        .scalar()
        or 0,
        freelancers=db.session.query(func.count(FreelancerProfile.id)).scalar() or 0,
        users=db.session.query(func.count(User.id)).scalar() or 0,
        proposals=db.session.query(func.count(Proposal.id)).scalar() or 0,
        reviews=db.session.query(func.count(Review.id)).scalar() or 0,
    )


# --------------------------------------------------------------------------- #
#  Authenticated endpoints
# --------------------------------------------------------------------------- #

@api_bp.route("/me")
@login_required
def me():
    user = current_user()
    if user is None:
        return jsonify(error="وارد نشده‌اید"), 401
    return jsonify(user_to_dict(user, detailed=True))


@api_bp.route("/my/proposals")
@login_required
def my_proposals():
    user = current_user()
    if user is None:
        return jsonify(error="وارد نشده‌اید"), 401
    return jsonify(items=[proposal_to_dict(p) for p in user.proposals])


@api_bp.route("/projects/<slug>/proposals")
@login_required
def project_proposals(slug: str):
    project = Project.query.filter_by(slug=slug).first()
    if project is None:
        return jsonify(error="پروژه یافت نشد"), 404

    user = current_user()
    if user is None:
        return jsonify(error="وارد نشده‌اید"), 401

    # The project owner sees every proposal; a freelancer sees only their own.
    if project.client_id == user.id:
        proposals = project.proposals
    else:
        proposals = [p for p in project.proposals if p.freelancer_id == user.id]

    return jsonify(items=[proposal_to_dict(p) for p in proposals])
