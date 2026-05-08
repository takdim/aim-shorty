from functools import wraps
from datetime import datetime
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.user import QuotaUsage
from app.models.subscription import PlanType, PLAN_LIMITS


def check_quota(user, quota_type: str) -> dict:
    """
    Check if a user is within their monthly quota for a given type.
    quota_type: 'links' | 'qrcodes'
    Returns dict: {allowed: bool, used: int, limit: int}
    """
    now   = datetime.utcnow()
    quota = QuotaUsage.query.filter_by(user_id=user.id, year=now.year, month=now.month).first()
    plan  = user.subscription.plan if user.subscription else PlanType.free
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.free])

    if quota_type == "links":
        used  = quota.links_used if quota else 0
        limit = limits["links_per_month"]
    elif quota_type == "qrcodes":
        used  = quota.qrcodes_used if quota else 0
        limit = limits["qrcodes_per_month"]
    else:
        return {"allowed": True, "used": 0, "limit": 0}

    return {"allowed": used < limit, "used": used, "limit": limit}


def require_plan(*plans):
    """Decorator to restrict a route to specific plans."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_plan = current_user.subscription.plan if current_user.subscription else PlanType.free
            if user_plan not in plans:
                flash("Fitur ini memerlukan upgrade paket.", "warning")
                return redirect(url_for("public.pricing"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    """Decorator to restrict route to admins only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Akses ditolak.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated
