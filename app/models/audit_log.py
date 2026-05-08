from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action      = db.Column(db.String(100), nullable=False)   # e.g. "user.suspend", "link.delete"
    entity_type = db.Column(db.String(50), nullable=True)     # e.g. "ShortLink", "User"
    entity_id   = db.Column(db.BigInteger, nullable=True)
    old_values  = db.Column(db.JSON, nullable=True)
    new_values  = db.Column(db.JSON, nullable=True)
    ip_address  = db.Column(db.String(45), nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by user={self.user_id}>"


class UrlBlacklist(db.Model):
    __tablename__ = "url_blacklist"

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    domain      = db.Column(db.String(255), nullable=True, index=True)
    url_pattern = db.Column(db.Text, nullable=True)
    reason      = db.Column(db.String(255), nullable=True)
    added_by    = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    admin = db.relationship("User", foreign_keys=[added_by])

    def __repr__(self) -> str:
        return f"<UrlBlacklist {self.domain or self.url_pattern}>"
