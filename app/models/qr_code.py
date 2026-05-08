from datetime import datetime
from app.extensions import db


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id            = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id       = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    short_link_id = db.Column(db.BigInteger, db.ForeignKey("short_links.id", ondelete="SET NULL"), nullable=True)
    name          = db.Column(db.String(255), nullable=False)
    target_url    = db.Column(db.Text, nullable=False)
    # style_config stores: dot_style, fg_color, bg_color, logo_url, corner_style, gradient, etc.
    style_config  = db.Column(db.JSON, nullable=True)
    file_path_png = db.Column(db.String(500), nullable=True)
    file_path_svg = db.Column(db.String(500), nullable=True)
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="qr_codes")
    short_link   = db.relationship("ShortLink", back_populates="qr_code")
    click_events = db.relationship("ClickEvent", back_populates="qr_code", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def total_scans(self) -> int:
        return self.click_events.count()

    def __repr__(self) -> str:
        return f"<QRCode {self.name}>"
