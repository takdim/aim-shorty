from datetime import datetime
from app.extensions import db


class ShortLink(db.Model):
    __tablename__ = "short_links"

    id           = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slug         = db.Column(db.String(50), nullable=False, unique=True, index=True)
    original_url = db.Column(db.Text, nullable=False)
    title        = db.Column(db.String(255), nullable=True)
    expires_at   = db.Column(db.DateTime, nullable=True)
    is_active    = db.Column(db.Boolean, nullable=False, default=True, index=True)
    utm_source   = db.Column(db.String(100), nullable=True)
    utm_medium   = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="short_links")
    qr_code      = db.relationship("QRCode", back_populates="short_link", uselist=False)
    click_events = db.relationship("ClickEvent", back_populates="short_link", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def total_clicks(self) -> int:
        return self.click_events.count()

    @property
    def short_url(self) -> str:
        from flask import current_app
        base = current_app.config.get("APP_BASE_URL", "http://localhost:5000")
        return f"{base}/{self.slug}"

    def __repr__(self) -> str:
        return f"<ShortLink /{self.slug}>"
