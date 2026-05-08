import enum
from datetime import datetime
from app.extensions import db


class DeviceType(enum.Enum):
    desktop = "desktop"
    mobile  = "mobile"
    tablet  = "tablet"
    unknown = "unknown"


class ClickSourceType(enum.Enum):
    short_link   = "short_link"
    qr_code      = "qr_code"
    landing_page = "landing_page"


class ClickEvent(db.Model):
    __tablename__ = "click_events"

    id              = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    short_link_id   = db.Column(db.BigInteger, db.ForeignKey("short_links.id",   ondelete="CASCADE"), nullable=True, index=True)
    qr_code_id      = db.Column(db.BigInteger, db.ForeignKey("qr_codes.id",      ondelete="CASCADE"), nullable=True, index=True)
    landing_page_id = db.Column(db.BigInteger, db.ForeignKey("landing_pages.id", ondelete="CASCADE"), nullable=True, index=True)
    source_type     = db.Column(db.Enum(ClickSourceType), nullable=False, index=True)
    ip_address      = db.Column(db.String(45), nullable=True)
    country_code    = db.Column(db.String(2), nullable=True)
    city            = db.Column(db.String(100), nullable=True)
    device_type     = db.Column(db.Enum(DeviceType), nullable=False, default=DeviceType.unknown)
    browser         = db.Column(db.String(100), nullable=True)
    os              = db.Column(db.String(100), nullable=True)
    referrer        = db.Column(db.Text, nullable=True)
    clicked_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    short_link   = db.relationship("ShortLink",   back_populates="click_events")
    qr_code      = db.relationship("QRCode",      back_populates="click_events")
    landing_page = db.relationship("LandingPage", back_populates="click_events")

    def __repr__(self) -> str:
        return f"<ClickEvent type={self.source_type.value} at={self.clicked_at}>"
