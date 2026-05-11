import enum
from datetime import datetime

from app.extensions import db


class PaymentGateway(enum.Enum):
    midtrans = "midtrans"
    doku = "doku"
    ipaymu = "ipaymu"


class AppSetting(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    PAYMENT_GATEWAY_KEY = "active_payment_gateway"
    DEFAULT_PAYMENT_GATEWAY = PaymentGateway.midtrans.value

    @classmethod
    def get_value(cls, key: str, default: str | None = None) -> str | None:
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            return default
        return setting.value

    @classmethod
    def set_value(cls, key: str, value: str) -> "AppSetting":
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        else:
            setting.value = value
        return setting

    @classmethod
    def get_payment_gateway(cls) -> PaymentGateway:
        value = cls.get_value(cls.PAYMENT_GATEWAY_KEY, cls.DEFAULT_PAYMENT_GATEWAY)
        try:
            return PaymentGateway(value)
        except ValueError:
            return PaymentGateway(cls.DEFAULT_PAYMENT_GATEWAY)

    def __repr__(self) -> str:
        return f"<AppSetting key={self.key}>"
