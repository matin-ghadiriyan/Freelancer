"""Freelancers blueprint: directory, detail, profile edit, skills, reviews."""

from __future__ import annotations

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import FreelancerProfile, Review, Skill, User
from app.routes.auth import current_user, login_required


freelancers_bp = Blueprint("freelancers", __name__, url_prefix="/freelancers")


# --------------------------------------------------------------------------- #
#  Directory
# --------------------------------------------------------------------------- #

@freelancers_bp.route("/")
def list_freelancers():
    page = request.args.get("page", 1, type=int)
    skill_slug = (request.args.get("skill") or "").strip()
    availability = (request.args.get("availability") or "").strip()

    query = FreelancerProfile.query.join(User).filter(User.is_active.is_(True))

    if skill_slug:
        query = query.join(FreelancerProfile.skills).filter(Skill.slug == skill_slug)
    if availability:
        query = query.filter(FreelancerProfile.availability == availability)

    pagination = query.order_by(
        FreelancerProfile.success_rate.desc(),
        FreelancerProfile.total_earned.desc(),
    ).paginate(page=page, per_page=12, error_out=False)

    skills = Skill.query.order_by(Skill.name).all()

    return render_template(
        "freelancers/list.html",
        pagination=pagination,
        freelancers=pagination.items,
        skills=skills,
        current_skill=skill_slug,
        current_availability=availability,
    )


# --------------------------------------------------------------------------- #
#  Detail
# --------------------------------------------------------------------------- #

@freelancers_bp.route("/<int:user_id>")
def detail(user_id: int):
    user = db.session.get(User, user_id)
    if user is None or user.freelancer_profile is None:
        abort(404)

    reviews = (
        Review.query.filter_by(target_id=user.id)
        .order_by(Review.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "freelancers/detail.html",
        freelancer=user,
        profile=user.freelancer_profile,
        reviews=reviews,
    )


# --------------------------------------------------------------------------- #
#  Own profile management
# --------------------------------------------------------------------------- #

@freelancers_bp.route("/me", methods=["GET", "POST"])
@login_required
def my_profile():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    profile = user.freelancer_profile
    skills = Skill.query.order_by(Skill.name).all()

    if request.method == "POST":
        headline = (request.form.get("headline") or "").strip()
        if not headline:
            flash("عنوان تخصص الزامی است.", "danger")
            return render_template(
                "freelancers/edit.html", profile=profile, skills=skills
            ), 400

        if profile is None:
            profile = FreelancerProfile(user_id=user.id, headline=headline)
            db.session.add(profile)
        else:
            profile.headline = headline

        profile.hourly_rate = request.form.get("hourly_rate", type=float)
        profile.experience_years = request.form.get("experience_years", type=int) or 0
        profile.availability = request.form.get("availability") or "available"
        profile.portfolio_url = (request.form.get("portfolio_url") or "").strip() or None

        skill_ids = request.form.getlist("skill_ids")
        if skill_ids:
            profile.skills = Skill.query.filter(
                Skill.id.in_([int(s) for s in skill_ids])
            ).all()

        db.session.commit()
        flash("پروفایل فریلنسری شما ذخیره شد.", "success")
        return redirect(url_for("freelancers.detail", user_id=user.id))

    return render_template("freelancers/edit.html", profile=profile, skills=skills)


# --------------------------------------------------------------------------- #
#  Reviews
# --------------------------------------------------------------------------- #

@freelancers_bp.route("/<int:user_id>/review", methods=["POST"])
@login_required
def add_review(user_id: int):
    target = db.session.get(User, user_id)
    if target is None:
        abort(404)

    author = current_user()
    if author is None:
        return redirect(url_for("auth.login"))

    if author.id == target.id:
        flash("نمی‌توانید برای خودتان نظر ثبت کنید.", "warning")
        return redirect(url_for("freelancers.detail", user_id=user_id))

    rating = request.form.get("rating", type=int)
    comment = (request.form.get("comment") or "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("امتیاز باید بین ۱ تا ۵ باشد.", "danger")
        return redirect(url_for("freelancers.detail", user_id=user_id))

    review = Review(
        rating=rating,
        comment=comment or None,
        author_id=author.id,
        target_id=target.id,
    )
    db.session.add(review)
    db.session.commit()
    flash("نظر شما ثبت شد. سپاسگزاریم!", "success")
    return redirect(url_for("freelancers.detail", user_id=user_id))
