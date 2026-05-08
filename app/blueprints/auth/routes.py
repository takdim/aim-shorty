from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.extensions import db, bcrypt
from app.models import User
from app.models.user import UserRole
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.models.user import QuotaUsage
from app.services.email_service import send_verification_email, send_reset_email
from app.utils.tokens import generate_token, verify_token
from app.utils.validators import is_valid_email
from datetime import datetime


# ─── Register ────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not name:
            errors.append("Nama wajib diisi.")
        if not is_valid_email(email):
            errors.append("Format email tidak valid.")
        if len(password) < 8:
            errors.append("Password minimal 8 karakter.")
        if password != confirm:
            errors.append("Password tidak cocok.")
        if User.query.filter_by(email=email).first():
            errors.append("Email sudah terdaftar.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("auth/register.html", name=name, email=email)

        # Create user
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, password_hash=hashed)
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        # Create free subscription
        sub = Subscription(
            user_id=user.id,
            plan=PlanType.free,
            status=SubscriptionStatus.active,
        )
        db.session.add(sub)

        # Create quota usage for current month
        now = datetime.utcnow()
        quota = QuotaUsage(user_id=user.id, year=now.year, month=now.month)
        db.session.add(quota)

        db.session.commit()

        # Send verification email
        token = generate_token(user.email, salt="email-verify")
        send_verification_email(user, token)

        flash("Akun berhasil dibuat! Cek email untuk verifikasi.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if not user or not user.password_hash or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Email atau password salah.", "danger")
            return render_template("auth/login.html", email=email)

        if not user.is_email_verified:
            flash("Silakan verifikasi email Anda terlebih dahulu.", "warning")
            return render_template("auth/login.html", email=email)

        login_user(user, remember=remember)
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html")


# ─── Logout ───────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("public.index"))


# ─── Email Verification ───────────────────────────────────────────────────────

@auth_bp.route("/verify-email/<token>")
def verify_email(token: str):
    email = verify_token(token, salt="email-verify", max_age=86400)
    if not email:
        flash("Link verifikasi tidak valid atau sudah kedaluwarsa.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_email_verified:
        flash("Email sudah diverifikasi.", "info")
    else:
        user.is_email_verified = True
        user.email_verified_at = datetime.utcnow()
        db.session.commit()
        flash("Email berhasil diverifikasi! Silakan login.", "success")

    return redirect(url_for("auth.login"))


# ─── Forgot Password ──────────────────────────────────────────────────────────

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show success to prevent user enumeration
        if user and user.password_hash:
            token = generate_token(user.email, salt="password-reset")
            send_reset_email(user, token)

        flash("Jika email terdaftar, link reset password telah dikirim.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


# ─── Reset Password ───────────────────────────────────────────────────────────

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    email = verify_token(token, salt="password-reset", max_age=3600)
    if not email:
        flash("Link reset tidak valid atau sudah kedaluwarsa.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password minimal 8 karakter.", "danger")
            return render_template("auth/reset_password.html", token=token)
        if password != confirm:
            flash("Password tidak cocok.", "danger")
            return render_template("auth/reset_password.html", token=token)

        user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        db.session.commit()
        flash("Password berhasil diubah. Silakan login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
