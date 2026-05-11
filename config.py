import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ──────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))

    # ── Database ───────────────────────────────────────────────────────────────
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "aim_shorty")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    RATELIMIT_STORAGE_URL = REDIS_URL

    # ── Email ──────────────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "LinkCraft <noreply@linkcraft.io>")

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 30 * 24 * 3600  # 30 days

    # ── Midtrans ──────────────────────────────────────────────────────────────
    MIDTRANS_SERVER_KEY = os.environ.get("MIDTRANS_SERVER_KEY", "")
    MIDTRANS_CLIENT_KEY = os.environ.get("MIDTRANS_CLIENT_KEY", "")
    MIDTRANS_IS_PRODUCTION = os.environ.get("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"

    # ── DOKU ──────────────────────────────────────────────────────────────────
    DOKU_MERCHANT_ID = os.environ.get("DOKU_MERCHANT_ID", "")
    DOKU_API_KEY = os.environ.get("DOKU_API_KEY", "")
    DOKU_API_SECRET = os.environ.get("DOKU_API_SECRET", "")
    DOKU_CLIENT_ID = os.environ.get("DOKU_CLIENT_ID", "")
    DOKU_IS_PRODUCTION = os.environ.get("DOKU_IS_PRODUCTION", "false").lower() == "true"

    # ── iPaymu ────────────────────────────────────────────────────────────────
    IPAYMU_VA = os.environ.get("IPAYMU_VA", "")
    IPAYMU_API_KEY = os.environ.get("IPAYMU_API_KEY", "")
    IPAYMU_IS_PRODUCTION = os.environ.get("IPAYMU_IS_PRODUCTION", "false").lower() == "true"

    # ── Pakasir ───────────────────────────────────────────────────────────────
    PAKASIR_PROJECT_SLUG = os.environ.get("PAKASIR_PROJECT_SLUG", "")
    PAKASIR_API_KEY = os.environ.get("PAKASIR_API_KEY", "")
    PAKASIR_IS_PRODUCTION = os.environ.get("PAKASIR_IS_PRODUCTION", "false").lower() == "true"
    PAKASIR_BASE_URL = os.environ.get("PAKASIR_BASE_URL", "https://app.pakasir.com")

    # ── App ────────────────────────────────────────────────────────────────────
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    CACHE_TYPE = "SimpleCache"       # Gunakan in-memory jika Redis tidak ada
    RATELIMIT_ENABLED = False        # Nonaktifkan rate limit saat dev


class ProductionConfig(Config):
    DEBUG = False
    WTF_CSRF_ENABLED = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
