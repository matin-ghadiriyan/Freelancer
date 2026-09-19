"""Admin blueprint: dashboard, manage users, projects, categories, skills, reviews."""

from __future__ import annotations

from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from app.extensions import db
from app.models import Category, FreelancerProfile, Project, Proposal, Review, Skill, User
from app.routes.auth import current_user, login_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# --------------------------------------------------------------------------- #
#  Access control
# --------------------------------------------------------------------------- #

def admin_required(view):
    """Allow only authenticated admins."""

    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None or not user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


# --------------------------------------------------------------------------- #
#  Dashboard
# --------------------------------------------------------------------------- #

@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "users": db.session.query(func.count(User.id)).scalar() or 0,
        "freelancers": db.session.query(func.count(FreelancerProfile.id)).scalar() or 0,
        "projects": db.session.query(func.count(Project.id)).scalar() or 0,
        "open_projects": db.session.query(func.count(Project.id))
        .filter(Project.status == "open")
        .scalar()
        or 0,
        "proposals": db.session.query(func.count(Proposal.id)).scalar() or 0,
        "reviews": db.session.query(func.count(Review.id)).scalar() or 0,
        "categories": db.session.query(func.count(Category.id)).scalar() or 0,
        "skills": db.session.query(func.count(Skill.id)).scalar() or 0,
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_projects=recent_projects,
    )


# --------------------------------------------------------------------------- #
#  Users
# --------------------------------------------------------------------------- #

@admin_bp.route("/users")
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/users.html", pagination=pagination, users=pagination.items)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.is_admin:
        flash("امکان غیرفعال‌سازی مدیر وجود ندارد.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    flash("وضعیت کاربر تغییر کرد.", "success")
    return redirect(url_for("admin.users"))


# --------------------------------------------------------------------------- #
#  Projects
# --------------------------------------------------------------------------- #

@admin_bp.route("/projects")
@admin_required
def projects():
    page = request.args.get("page", 1, type=int)
    pagination = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/projects.html", pagination=pagination, projects=pagination.items
    )


@admin_bp.route("/projects/<int:project_id>/feature", methods=["POST"])
@admin_required
def toggle_feature(project_id: int):
    project = db.session.get(Project, project_id)
    if project is None:
        abort(404)
    project.is_featured = not project.is_featured
    db.session.commit()
    flash("وضعیت ویژه بودن پروژه تغییر کرد.", "success")
    return redirect(url_for("admin.projects"))


# --------------------------------------------------------------------------- #
#  Categories
# --------------------------------------------------------------------------- #

@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        slug = (request.form.get("slug") or "").strip()
        if not name or not slug:
            flash("نام و اسلاگ دسته‌بندی الزامی است.", "danger")
            return redirect(url_for("admin.categories"))
        if Category.query.filter_by(slug=slug).first():
            flash("این اسلاگ قبلاً استفاده شده است.", "danger")
            return redirect(url_for("admin.categories"))

        db.session.add(
            Category(
                name=name,
                slug=slug,
                description=(request.form.get("description") or "").strip() or None,
                icon=(request.form.get("icon") or "").strip() or None,
            )
        )
        db.session.commit()
        flash("دسته‌بندی اضافه شد.", "success")
        return redirect(url_for("admin.categories"))

    all_categories = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=all_categories)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def delete_category(category_id: int):
    category = db.session.get(Category, category_id)
    if category is None:
        abort(404)
    db.session.delete(category)
    db.session.commit()
    flash("دسته‌بندی حذف شد.", "info")
    return redirect(url_for("admin.categories"))


# --------------------------------------------------------------------------- #
#  Skills
# --------------------------------------------------------------------------- #

@admin_bp.route("/skills", methods=["GET", "POST"])
@admin_required
def skills():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        slug = (request.form.get("slug") or "").strip()
        if not name or not slug:
            flash("نام و اسلاگ مهارت الزامی است.", "danger")
            return redirect(url_for("admin.skills"))
        if Skill.query.filter_by(slug=slug).first():
            flash("این اسلاگ قبلاً استفاده شده است.", "danger")
            return redirect(url_for("admin.skills"))

        db.session.add(
            Skill(
                name=name,
                slug=slug,
                icon=(request.form.get("icon") or "").strip() or None,
            )
        )
        db.session.commit()
        flash("مهارت اضافه شد.", "success")
        return redirect(url_for("admin.skills"))

    all_skills = Skill.query.order_by(Skill.name).all()
    return render_template("admin/skills.html", skills=all_skills)


@admin_bp.route("/skills/<int:skill_id>/delete", methods=["POST"])
@admin_required
def delete_skill(skill_id: int):
    skill = db.session.get(Skill, skill_id)
    if skill is None:
        abort(404)
    db.session.delete(skill)
    db.session.commit()
    flash("مهارت حذف شد.", "info")
    return redirect(url_for("admin.skills"))


# --------------------------------------------------------------------------- #
#  Reviews moderation
# --------------------------------------------------------------------------- #

@admin_bp.route("/reviews")
@admin_required
def reviews():
    page = request.args.get("page", 1, type=int)
    pagination = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/reviews.html", pagination=pagination, reviews=pagination.items)


@admin_bp.route("/reviews/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_review(review_id: int):
    review = db.session.get(Review, review_id)
    if review is None:
        abort(404)
    db.session.delete(review)
    db.session.commit()
    flash("نظر حذف شد.", "info")
    return redirect(url_for("admin.reviews"))
