"""Projects blueprint: listing, detail, create, proposals."""

from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import or_

from app.extensions import db
from app.models import Category, Project, Proposal, Skill
from app.routes.auth import current_user, login_required


projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _slugify(text: str) -> str:
    base = "".join(c if c.isalnum() or c in "-_" else "-" for c in text.strip().lower())
    while "--" in base:
        base = base.replace("--", "-")
    return base.strip("-") or "project"


def _unique_slug(title: str) -> str:
    slug = _slugify(title)
    candidate = slug
    counter = 1
    while Project.query.filter_by(slug=candidate).first():
        counter += 1
        candidate = f"{slug}-{counter}"
    return candidate


# --------------------------------------------------------------------------- #
#  Public listing / detail
# --------------------------------------------------------------------------- #

@projects_bp.route("/")
def list_projects():
    page = request.args.get("page", 1, type=int)
    category_slug = (request.args.get("category") or "").strip()
    level = (request.args.get("level") or "").strip()
    kind = (request.args.get("type") or "").strip()

    query = Project.query.filter_by(status="open")

    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)
    if level:
        query = query.filter(Project.experience_level == level)
    if kind:
        query = query.filter(Project.project_type == kind)

    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "projects/list.html",
        pagination=pagination,
        projects=pagination.items,
        categories=categories,
        current_category=category_slug,
        current_level=level,
        current_type=kind,
    )


@projects_bp.route("/<slug>")
def detail(slug: str):
    project = Project.query.filter_by(slug=slug).first()
    if project is None:
        abort(404)

    project.views = (project.views or 0) + 1
    db.session.commit()

    user = current_user()
    my_proposal = None
    if user is not None:
        my_proposal = Proposal.query.filter_by(
            project_id=project.id, freelancer_id=user.id
        ).first()

    related = (
        Project.query.filter(
            Project.id != project.id,
            Project.status == "open",
            or_(
                Project.category_id == project.category_id,
                Project.experience_level == project.experience_level,
            ),
        )
        .order_by(Project.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "projects/detail.html",
        project=project,
        my_proposal=my_proposal,
        related=related,
    )


# --------------------------------------------------------------------------- #
#  Create
# --------------------------------------------------------------------------- #

@projects_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    categories = Category.query.order_by(Category.name).all()
    skills = Skill.query.order_by(Skill.name).all()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()

        if not title or not description:
            flash("عنوان و توضیحات پروژه الزامی است.", "danger")
            return render_template("projects/create.html", categories=categories, skills=skills), 400

        deadline_raw = (request.form.get("deadline") or "").strip()
        deadline = None
        if deadline_raw:
            try:
                deadline = datetime.strptime(deadline_raw, "%Y-%m-%d").date()
            except ValueError:
                deadline = None

        def _to_decimal(field: str):
            raw = (request.form.get(field) or "").strip()
            if not raw:
                return None
            try:
                return float(raw)
            except ValueError:
                return None

        project = Project(
            title=title,
            slug=_unique_slug(title),
            description=description,
            budget_min=_to_decimal("budget_min"),
            budget_max=_to_decimal("budget_max"),
            deadline=deadline,
            experience_level=(request.form.get("experience_level") or "intermediate"),
            project_type=(request.form.get("project_type") or "fixed"),
            category_id=request.form.get("category_id", type=int),
            client_id=user.id,
        )

        skill_ids = request.form.getlist("skill_ids")
        if skill_ids:
            project.skills = Skill.query.filter(Skill.id.in_([int(s) for s in skill_ids])).all()

        db.session.add(project)
        db.session.commit()
        flash("پروژه با موفقیت ثبت شد.", "success")
        return redirect(url_for("projects.detail", slug=project.slug))

    return render_template("projects/create.html", categories=categories, skills=skills)


# --------------------------------------------------------------------------- #
#  Proposals
# --------------------------------------------------------------------------- #

@projects_bp.route("/<slug>/proposal", methods=["POST"])
@login_required
def submit_proposal(slug: str):
    project = Project.query.filter_by(slug=slug).first()
    if project is None:
        abort(404)

    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    if project.client_id == user.id:
        flash("نمی‌توانید برای پروژه خودتان پیشنهاد ارسال کنید.", "warning")
        return redirect(url_for("projects.detail", slug=project.slug))

    existing = Proposal.query.filter_by(project_id=project.id, freelancer_id=user.id).first()
    if existing:
        flash("شما قبلاً برای این پروژه پیشنهاد ارسال کرده‌اید.", "warning")
        return redirect(url_for("projects.detail", slug=project.slug))

    cover_letter = (request.form.get("cover_letter") or "").strip()
    bid_amount = request.form.get("bid_amount", type=float)
    delivery_days = request.form.get("delivery_days", type=int)

    if not cover_letter or not bid_amount:
        flash("متن پیشنهاد و مبلغ پیشنهادی الزامی است.", "danger")
        return redirect(url_for("projects.detail", slug=project.slug))

    proposal = Proposal(
        cover_letter=cover_letter,
        bid_amount=bid_amount,
        delivery_days=delivery_days,
        project_id=project.id,
        freelancer_id=user.id,
    )
    db.session.add(proposal)
    db.session.commit()
    flash("پیشنهاد شما با موفقیت ارسال شد.", "success")
    return redirect(url_for("projects.detail", slug=project.slug))


@projects_bp.route("/proposals/<int:proposal_id>/<action>")
@login_required
def manage_proposal(proposal_id: int, action: str):
    proposal = db.session.get(Proposal, proposal_id)
    if proposal is None:
        abort(404)

    project = proposal.project
    user = current_user()

    if user is None or project.client_id != user.id:
        abort(403)

    if action == "accept":
        proposal.status = "accepted"
        project.status = "in_progress"
        for other in project.proposals:
            if other.id != proposal.id and other.status == "pending":
                other.status = "rejected"
        flash("پیشنهاد پذیرفته شد و پروژه در حال انجام قرار گرفت.", "success")
    elif action == "reject":
        proposal.status = "rejected"
        flash("پیشنهاد رد شد.", "info")
    else:
        abort(404)

    db.session.commit()
    return redirect(url_for("projects.detail", slug=project.slug))
