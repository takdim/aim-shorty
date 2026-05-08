from datetime import datetime
from app.extensions import db


class LandingPage(db.Model):
    __tablename__ = "landing_pages"

    id           = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slug         = db.Column(db.String(100), nullable=False, unique=True, index=True)
    title        = db.Column(db.String(255), nullable=False)
    bio          = db.Column(db.Text, nullable=True)
    avatar_url   = db.Column(db.String(500), nullable=True)
    # theme_config: bg_color, font, button_style, text_color, etc.
    theme_config = db.Column(db.JSON, nullable=True)
    is_published = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user         = db.relationship("User", back_populates="landing_pages")
    page_links   = db.relationship(
        "PageLink",
        back_populates="landing_page",
        order_by="PageLink.sort_order",
        cascade="all, delete-orphan",
    )
    click_events = db.relationship("ClickEvent", back_populates="landing_page", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def public_url(self) -> str:
        from flask import current_app
        base = current_app.config.get("APP_BASE_URL", "http://localhost:5000")
        return f"{base}/p/{self.slug}"

    def __repr__(self) -> str:
        return f"<LandingPage /{self.slug}>"


class PageLink(db.Model):
    __tablename__ = "page_links"

    id              = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    landing_page_id = db.Column(db.BigInteger, db.ForeignKey("landing_pages.id", ondelete="CASCADE"), nullable=False, index=True)
    label           = db.Column(db.String(255), nullable=False)
    url             = db.Column(db.Text, nullable=False)
    icon            = db.Column(db.String(100), nullable=True)
    sort_order      = db.Column(db.Integer, nullable=False, default=0)
    is_active       = db.Column(db.Boolean, nullable=False, default=True)
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    landing_page = db.relationship("LandingPage", back_populates="page_links")

    def __repr__(self) -> str:
        return f"<PageLink {self.label}>"
