import enum
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"
    support = "support"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id                = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email             = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash     = db.Column(db.String(255), nullable=True)       # NULL jika OAuth only
    name              = db.Column(db.String(100), nullable=False)
    avatar_url        = db.Column(db.String(500), nullable=True)
    role              = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    last_login_at     = db.Column(db.DateTime, nullable=True)
    created_at        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription  = db.relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quota_usage   = db.relationship("QuotaUsage",   back_populates="user", uselist=False, cascade="all, delete-orphan")
    short_links   = db.relationship("ShortLink",    back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    qr_codes      = db.relationship("QRCode",       back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    landing_pages = db.relationship("LandingPage",  back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    audit_logs    = db.relationship("AuditLog",     back_populates="user", lazy="dynamic")

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def is_admin(self) -> bool:
        return self.role in (UserRole.admin, UserRole.superadmin)

    @property
    def plan(self) -> str:
        if self.subscription:
            return self.subscription.plan.value
        return "free"

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class QuotaUsage(db.Model):
    __tablename__ = "quota_usages"
    __table_args__ = (
        db.UniqueConstraint("user_id", "year", "month", name="uq_quota_user_month"),
    )

    id           = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    year         = db.Column(db.Integer, nullable=False)
    month        = db.Column(db.Integer, nullable=False)
    links_used   = db.Column(db.Integer, nullable=False, default=0)
    qrcodes_used = db.Column(db.Integer, nullable=False, default=0)
    pages_used   = db.Column(db.Integer, nullable=False, default=0)
    updated_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="quota_usage")

    def __repr__(self) -> str:
        return f"<QuotaUsage user={self.user_id} {self.year}/{self.month}>"


# ── Login manager loader ───────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
