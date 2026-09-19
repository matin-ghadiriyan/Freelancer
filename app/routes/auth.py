"""Authentication blueprint: register, login, logout, profile."""

from __future__ import annotations

from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import or_

from app.extensions import db
from app.models import FreelancerProfile, User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def current_user() -> User | None:
    """Return the logged-in user from the session, if any."""
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def login_required(view):
    """Very small decorator to protect views."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("برای ادامه ابتدا وارد حساب خود شوید.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


# --------------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------------- #

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""
        role = (request.form.get("role") or "client").strip()

        errors: list[str] = []
        if not full_name:
            errors.append("نام کامل را وارد کنید.")
        if not email or "@" not in email:
            errors.append("ایمیل معتبر وارد کنید.")
        if len(password) < 6:
            errors.append("رمز عبور باید حداقل ۶ کاراکتر باشد.")
        if password != confirm:
            errors.append("تکرار رمز عبور مطابقت ندارد.")
        if User.query.filter_by(email=email).first():
            errors.append("این ایمیل قبلاً ثبت شده است.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/register.html", form=request.form), 400

        user = User(full_name=full_name, email=email, bio=request.form.get("bio"))
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == "freelancer":
            profile = FreelancerProfile(
                user_id=user.id,
                headline=(request.form.get("headline") or "فریلنسر تازه‌کار").strip(),
            )
            db.session.add(profile)

        db.session.commit()
        session["user_id"] = user.id
        flash("حساب شما با موفقیت ساخته شد. خوش آمدید!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        identifier = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter(or_(User.email == identifier)).first()

        if user and user.check_password(password) and user.is_active:
            session.clear()
            session["user_id"] = user.id
            flash(f"خوش آمدید {user.full_name}!", "success")
            # Only allow internal redirects to avoid open-redirect attacks.
            next_url = request.args.get("next") or ""
            if not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("main.dashboard")
            return redirect(next_url)

        flash("ایمیل یا رمز عبور نادرست است.", "danger")
        return render_template("auth/login.html", form=request.form), 401

    return render_template("auth/login.html", form={})


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("با موفقیت خارج شدید.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        user.full_name = (request.form.get("full_name") or user.full_name).strip()
        user.bio = request.form.get("bio") or user.bio
        user.country = request.form.get("country") or user.country
        user.phone = request.form.get("phone") or user.phone
        db.session.commit()
        flash("پروفایل با موفقیت به‌روزرسانی شد.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", user=user)
