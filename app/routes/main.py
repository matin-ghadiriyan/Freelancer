"""Main blueprint: landing page, dashboard, about, contact, search."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from app.extensions import db
from app.models import Category, FreelancerProfile, Project, Skill, User
from app.routes.auth import current_user, login_required


main_bp = Blueprint("main", __name__)


# --------------------------------------------------------------------------- #
#  Public pages
# --------------------------------------------------------------------------- #

@main_bp.route("/")
def index():
    """Professional landing page with featured projects + top freelancers."""
    featured = (
        Project.query.filter_by(status="open", is_featured=True)
        .order_by(Project.created_at.desc())
        .limit(6)
        .all()
    )
    latest = (
        Project.query.filter_by(status="open")
        .order_by(Project.created_at.desc())
        .limit(8)
        .all()
    )
    top_freelancers = (
        FreelancerProfile.query.join(User)
        .filter(User.is_active.is_(True))
        .order_by(FreelancerProfile.success_rate.desc(), FreelancerProfile.total_earned.desc())
        .limit(6)
        .all()
    )
    categories = Category.query.order_by(Category.name).limit(8).all()

    stats = {
        "projects": db.session.query(func.count(Project.id)).scalar() or 0,
        "freelancers": db.session.query(func.count(FreelancerProfile.id)).scalar() or 0,
        "clients": db.session.query(func.count(User.id)).scalar() or 0,
        "skills": db.session.query(func.count(Skill.id)).scalar() or 0,
    }

    return render_template(
        "main/index.html",
        featured=featured,
        latest=latest,
        top_freelancers=top_freelancers,
        categories=categories,
        stats=stats,
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("message") or "").strip()
        if not name or not email or not message:
            flash("لطفاً همه فیلدها را پر کنید.", "danger")
            return render_template("main/contact.html"), 400
        flash("پیام شما ارسال شد. به‌زودی پاسخ می‌دهیم.", "success")
        return redirect(url_for("main.contact"))
    return render_template("main/contact.html")


# --------------------------------------------------------------------------- #
#  Dashboard
# --------------------------------------------------------------------------- #

@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    my_projects = (
        Project.query.filter_by(client_id=user.id)
        .order_by(Project.created_at.desc())
        .limit(10)
        .all()
    )
    my_proposals = list(user.proposals)[:10]
    my_profile = user.freelancer_profile

    summary = {
        "projects_count": len(user.posted_projects),
        "proposals_count": len(user.proposals),
        "rating": user.average_rating,
    }

    return render_template(
        "main/dashboard.html",
        user=user,
        my_projects=my_projects,
        my_proposals=my_proposals,
        my_profile=my_profile,
        summary=summary,
    )


# --------------------------------------------------------------------------- #
#  Search
# --------------------------------------------------------------------------- #

@main_bp.route("/search")
def search():
    q = (request.args.get("q") or "").strip()
    kind = (request.args.get("kind") or "projects").strip()

    results = []
    if q:
        if kind == "freelancers":
            results = (
                FreelancerProfile.query.join(User)
                .filter(
                    db.or_(
                        FreelancerProfile.headline.ilike(f"%{q}%"),
                        User.full_name.ilike(f"%{q}%"),
                    )
                )
                .limit(30)
                .all()
            )
        else:
            results = (
                Project.query.filter(
                    db.or_(
                        Project.title.ilike(f"%{q}%"),
                        Project.description.ilike(f"%{q}%"),
                    )
                )
                .order_by(Project.created_at.desc())
                .limit(30)
                .all()
            )

    return render_template("main/search.html", q=q, kind=kind, results=results)
