import shortuuid
from datetime import datetime
from app.extensions import db
from app.models import ShortLink
from app.models.user import QuotaUsage
from app.utils.validators import is_valid_url, is_blacklisted


def generate_slug(length: int = 6) -> str:
    """Generate a unique random slug."""
    while True:
        slug = shortuuid.ShortUUID().random(length=length)
        if not ShortLink.query.filter_by(slug=slug).first():
            return slug


def create_short_link(
    user,
    original_url: str,
    custom_alias: str | None = None,
    expires_at: str | None = None,
    title: str | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
) -> tuple:
    """
    Create a short link for a user.
    Returns (ShortLink, None) on success or (None, error_message) on failure.
    """
    # Validate URL
    if not original_url:
        return None, "URL tidak boleh kosong."
    if not is_valid_url(original_url):
        return None, "Format URL tidak valid."
    if is_blacklisted(original_url):
        return None, "URL ini diblokir oleh sistem."

    # Resolve slug
    if custom_alias:
        slug = custom_alias.lower().strip()
        if ShortLink.query.filter_by(slug=slug).first():
            return None, f"Alias '{slug}' sudah digunakan."
    else:
        slug = generate_slug()

    # Parse expires_at
    parsed_expires = None
    if expires_at:
        try:
            parsed_expires = datetime.fromisoformat(expires_at)
        except ValueError:
            return None, "Format tanggal kedaluwarsa tidak valid."

    link = ShortLink(
        user_id=user.id,
        slug=slug,
        original_url=original_url,
        title=title,
        expires_at=parsed_expires,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
    )
    db.session.add(link)

    # Increment quota
    now = datetime.utcnow()
    quota = QuotaUsage.query.filter_by(user_id=user.id, year=now.year, month=now.month).first()
    if quota:
        quota.links_used += 1

    db.session.commit()
    return link, None
