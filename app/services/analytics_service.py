from flask import request as flask_request
from app.extensions import db
from app.models.click_event import ClickEvent, ClickSourceType, DeviceType
from datetime import datetime

try:
    from user_agents import parse as parse_ua
    HAS_UA = True
except ImportError:
    HAS_UA = False


def log_click(
    source_type: ClickSourceType,
    request,
    short_link_id: int | None = None,
    qr_code_id: int | None = None,
    landing_page_id: int | None = None,
) -> None:
    """Log a click/scan/view event from a request."""
    ip        = _get_ip(request)
    referrer  = request.referrer or None
    ua_string = request.headers.get("User-Agent", "")

    browser = "Unknown"
    os_name = "Unknown"
    device  = DeviceType.unknown

    if HAS_UA and ua_string:
        ua = parse_ua(ua_string)
        browser  = ua.browser.family
        os_name  = ua.os.family
        if ua.is_mobile:
            device = DeviceType.mobile
        elif ua.is_tablet:
            device = DeviceType.tablet
        elif ua.is_pc:
            device = DeviceType.desktop

    event = ClickEvent(
        short_link_id=short_link_id,
        qr_code_id=qr_code_id,
        landing_page_id=landing_page_id,
        source_type=source_type,
        ip_address=ip,
        device_type=device,
        browser=browser,
        os=os_name,
        referrer=referrer,
        clicked_at=datetime.utcnow(),
    )
    db.session.add(event)
    db.session.commit()


def _get_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"
