from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models import User, ShortLink, QRCode
from app.models.user import UserRole
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.models.click_event import ClickEvent
from datetime import datetime


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("Akses ditolak.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated


# ── Overview ──────────────────────────────────────────────────────────────────
@admin_bp.route("/")
@admin_required
def index():
    total_users  = User.query.count()
    total_links  = ShortLink.query.count()
    total_qrs    = QRCode.query.count()
    total_clicks = ClickEvent.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    return render_template(
        "admin/index.html",
        total_users=total_users,
        total_links=total_links,
        total_qrcodes=total_qrs,
        total_clicks=total_clicks,
        recent_users=recent_users,
    )


# ── Users ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/users")
@admin_required
def users():
    page   = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    query  = User.query.order_by(User.created_at.desc())
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.name.ilike(f"%{search}%"))
        )
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/users.html", pagination=pagination, search=search)


@admin_bp.route("/users/<int:user_id>/toggle-suspend", methods=["POST"])
@admin_required
def toggle_suspend(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("User tidak ditemukan.", "danger")
        return redirect(url_for("admin.users"))
    if user.role == UserRole.superadmin or user.id == current_user.id:
        flash("Tidak bisa mengubah status akun ini.", "danger")
    else:
        user.is_email_verified = not user.is_email_verified
        status = "diaktifkan" if user.is_email_verified else "di-suspend"
        db.session.commit()
        flash(f"Akun {user.email} berhasil {status}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/set-plan", methods=["POST"])
@admin_required
def set_plan(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("User tidak ditemukan.", "danger")
        return redirect(url_for("admin.users"))
    plan_value = request.form.get("plan", "free")
    try:
        new_plan = PlanType(plan_value)
    except ValueError:
        flash("Paket tidak valid.", "danger")
        return redirect(url_for("admin.users"))
    sub = user.subscription
    if sub:
        sub.plan = new_plan
        sub.status = SubscriptionStatus.active
        if new_plan != PlanType.free:
            from datetime import timedelta
            sub.current_period_start = datetime.utcnow()
            sub.current_period_end   = datetime.utcnow() + timedelta(days=30)
        db.session.commit()
        flash(f"Paket {user.email} diubah ke {new_plan.value.capitalize()}.", "success")
    else:
        flash("User tidak memiliki subscription record.", "danger")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user or user.role == UserRole.superadmin or user.id == current_user.id:
        flash("Tidak bisa menghapus akun ini.", "danger")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"Akun {user.email} berhasil dihapus.", "success")
    return redirect(url_for("admin.users"))


# ── Links ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/links")
@admin_required
def links():
    page   = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    query  = ShortLink.query.order_by(ShortLink.created_at.desc())
    if search:
        query = query.filter(
            (ShortLink.slug.ilike(f"%{search}%")) |
            (ShortLink.original_url.ilike(f"%{search}%"))
        )
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/links.html", pagination=pagination, search=search)


@admin_bp.route("/links/<int:link_id>/toggle", methods=["POST"])
@admin_required
def toggle_link(link_id: int):
    link = db.session.get(ShortLink, link_id)
    if link:
        link.is_active = not link.is_active
        db.session.commit()
        status = "diaktifkan" if link.is_active else "dinonaktifkan"
        flash(f"Link /{link.slug} berhasil {status}.", "success")
    return redirect(url_for("admin.links"))


@admin_bp.route("/links/<int:link_id>/delete", methods=["POST"])
@admin_required
def delete_link(link_id: int):
    link = db.session.get(ShortLink, link_id)
    if link:
        db.session.delete(link)
        db.session.commit()
        flash(f"Link /{link.slug} berhasil dihapus.", "success")
    return redirect(url_for("admin.links"))


# ── QR Codes ──────────────────────────────────────────────────────────────────
@admin_bp.route("/qr-codes")
@admin_required
def qr_codes():
    page       = request.args.get("page", 1, type=int)
    pagination = QRCode.query.order_by(QRCode.created_at.desc()).paginate(page=page, per_page=24, error_out=False)
    return render_template("admin/qr_codes.html", pagination=pagination)


@admin_bp.route("/qr-codes/<int:qr_id>/delete", methods=["POST"])
@admin_required
def delete_qr(qr_id: int):
    qr = db.session.get(QRCode, qr_id)
    if qr:
        db.session.delete(qr)
        db.session.commit()
        flash("QR Code berhasil dihapus.", "success")
    return redirect(url_for("admin.qr_codes"))
