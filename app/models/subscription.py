import enum
from datetime import datetime
from app.extensions import db


class PlanType(enum.Enum):
    free    = "free"
    starter = "starter"
    pro     = "pro"


class SubscriptionStatus(enum.Enum):
    active    = "active"
    cancelled = "cancelled"
    past_due  = "past_due"
    trialing  = "trialing"


# ── Plan limits config ─────────────────────────────────────────────────────────
PLAN_LIMITS = {
    PlanType.free: {
        "links_per_month":   80,
        "qrcodes_per_month": 5,
        "pages_total":       5,
        "analytics_days":    0,
        "bulk_creation":     False,
        "csv_export":        False,
    },
    PlanType.starter: {
        "links_per_month":   140,
        "qrcodes_per_month": 15,
        "pages_total":       10,
        "analytics_days":    30,
        "bulk_creation":     False,
        "csv_export":        False,
    },
    PlanType.pro: {
        "links_per_month":   300,
        "qrcodes_per_month": 30,
        "pages_total":       20,
        "analytics_days":    365,
        "bulk_creation":     True,
        "csv_export":        True,
    },
}


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id                     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id                = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan                   = db.Column(db.Enum(PlanType), nullable=False, default=PlanType.free)
    status                 = db.Column(db.Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.active)
    midtrans_order_id      = db.Column(db.String(100), nullable=True)
    midtrans_token         = db.Column(db.String(100), nullable=True)
    current_period_start   = db.Column(db.DateTime, nullable=True)
    current_period_end     = db.Column(db.DateTime, nullable=True)
    cancelled_at           = db.Column(db.DateTime, nullable=True)
    created_at             = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at             = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="subscription")

    @property
    def limits(self) -> dict:
        return PLAN_LIMITS.get(self.plan, PLAN_LIMITS[PlanType.free])

    def __repr__(self) -> str:
        return f"<Subscription user={self.user_id} plan={self.plan.value}>"
