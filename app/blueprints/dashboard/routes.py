from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard_bp
from app.extensions import db
from app.models import ShortLink, QRCode, LandingPage, ClickEvent
from app.models.click_event import ClickSourceType
from datetime import datetime


# ─── Constants ────────────────────────────────────────────────────────────────

SOCIAL_PLATFORMS = [
    {"id": "instagram",  "label": "Instagram",   "icon": "instagram-logo",  "placeholder": "https://instagram.com/username"},
    {"id": "tiktok",     "label": "TikTok",      "icon": "tiktok-logo",     "placeholder": "https://tiktok.com/@username"},
    {"id": "whatsapp",   "label": "WhatsApp",    "icon": "whatsapp-logo",   "placeholder": "https://wa.me/628xxxxxxxxx"},
    {"id": "twitter",    "label": "Twitter / X", "icon": "twitter-logo",    "placeholder": "https://twitter.com/username"},
    {"id": "facebook",   "label": "Facebook",    "icon": "facebook-logo",   "placeholder": "https://facebook.com/yourpage"},
    {"id": "youtube",    "label": "YouTube",     "icon": "youtube-logo",    "placeholder": "https://youtube.com/@channel"},
    {"id": "telegram",   "label": "Telegram",    "icon": "telegram-logo",   "placeholder": "https://t.me/username"},
    {"id": "linkedin",   "label": "LinkedIn",    "icon": "linkedin-logo",   "placeholder": "https://linkedin.com/in/username"},
    {"id": "github",     "label": "GitHub",      "icon": "github-logo",     "placeholder": "https://github.com/username"},
    {"id": "pinterest",  "label": "Pinterest",   "icon": "pinterest-logo",  "placeholder": "https://pinterest.com/username"},
    {"id": "snapchat",   "label": "Snapchat",    "icon": "snapchat-logo",   "placeholder": "https://snapchat.com/add/username"},
    {"id": "shopee",     "label": "Shopee",      "icon": None,              "placeholder": "https://shopee.co.id/..."},
    {"id": "tokopedia",  "label": "Tokopedia",   "icon": None,              "placeholder": "https://tokopedia.com/..."},
    {"id": "custom",     "label": "Link Custom", "icon": None,              "placeholder": "https://websitesaya.com"},
]

_PLATFORM_MAP = {p["id"]: p for p in SOCIAL_PLATFORMS}

LANDING_TEMPLATES = [
    {"id": "minimal_dark",  "name": "Minimal Dark",  "bg": "#0f0f17", "btn": "#6366f1", "text": "#e2e8f0", "btn_style": "pill"},
    {"id": "minimal_light", "name": "Minimal Light", "bg": "#f8fafc", "btn": "#1e293b", "text": "#1e293b", "btn_style": "pill"},
    {"id": "purple_glow",   "name": "Purple Glow",   "bg": "#13002e", "btn": "#a855f7", "text": "#f3e8ff", "btn_style": "pill"},
    {"id": "teal_fresh",    "name": "Teal Fresh",    "bg": "#042f2e", "btn": "#14b8a6", "text": "#ccfbf1", "btn_style": "pill"},
    {"id": "warm_sunset",   "name": "Warm Sunset",   "bg": "#431407", "btn": "#f97316", "text": "#fff7ed", "btn_style": "pill"},
    {"id": "midnight_blue", "name": "Midnight Blue", "bg": "#0a192f", "btn": "#38bdf8", "text": "#e0f2fe", "btn_style": "pill"},
    {"id": "rose_blush",    "name": "Rose Blush",    "bg": "#fff1f2", "btn": "#f43f5e", "text": "#450a20", "btn_style": "pill"},
    {"id": "clean_outline", "name": "Clean Outline", "bg": "#ffffff", "btn": "#6366f1", "text": "#0f172a", "btn_style": "outline"},
]


# ─── Home ─────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/")
@login_required
def index():
    now = datetime.utcnow()
    quota = _get_or_create_quota(current_user, now)
    limits = current_user.subscription.limits if current_user.subscription else {}

    # Stats bulan ini
    recent_links = current_user.short_links.order_by(ShortLink.created_at.desc()).limit(5).all()
    recent_qrs   = current_user.qr_codes.order_by(QRCode.created_at.desc()).limit(5).all()

    total_clicks = (
        ClickEvent.query
        .join(ShortLink, ClickEvent.short_link_id == ShortLink.id)
        .filter(ShortLink.user_id == current_user.id)
        .filter(ClickEvent.source_type == ClickSourceType.short_link)
        .count()
    )

    return render_template(
        "dashboard/index.html",
        quota=quota,
        limits=limits,
        recent_links=recent_links,
        recent_qrs=recent_qrs,
        total_clicks=total_clicks,
    )


# ─── Links ────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/links")
@login_required
def links():
    page     = request.args.get("page", 1, type=int)
    search   = request.args.get("q", "").strip()
    status   = request.args.get("status", "")

    query = current_user.short_links.order_by(ShortLink.created_at.desc())

    if search:
        query = query.filter(
            (ShortLink.title.ilike(f"%{search}%")) |
            (ShortLink.slug.ilike(f"%{search}%")) |
            (ShortLink.original_url.ilike(f"%{search}%"))
        )
    if status == "active":
        query = query.filter_by(is_active=True)
    elif status == "inactive":
        query = query.filter_by(is_active=False)

    pagination = query.paginate(page=page, per_page=15, error_out=False)
    return render_template("dashboard/links.html", pagination=pagination, search=search, status=status)


@dashboard_bp.route("/links/create", methods=["POST"])
@login_required
def create_link():
    from app.services.link_service import create_short_link
    from app.utils.decorators import check_quota

    result = check_quota(current_user, "links")
    if not result["allowed"]:
        flash(f"Kuota link bulan ini sudah habis ({result['used']}/{result['limit']}). Upgrade paket Anda.", "danger")
        return redirect(url_for("dashboard.links"))

    original_url = request.form.get("original_url", "").strip()
    custom_alias = request.form.get("custom_alias", "").strip() or None
    expires_at   = request.form.get("expires_at") or None
    title        = request.form.get("title", "").strip() or None

    link, error = create_short_link(
        user=current_user,
        original_url=original_url,
        custom_alias=custom_alias,
        expires_at=expires_at,
        title=title,
    )

    if error:
        flash(error, "danger")
    else:
        flash(f"Short link berhasil dibuat: {link.short_url}", "success")

    return redirect(url_for("dashboard.links"))


@dashboard_bp.route("/links/<int:link_id>/delete", methods=["POST"])
@login_required
def delete_link(link_id: int):
    link = ShortLink.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    flash("Short link dihapus.", "success")
    return redirect(url_for("dashboard.links"))


@dashboard_bp.route("/links/toggle", methods=["POST"])
@login_required
def toggle_link(link_id: int):
    link = ShortLink.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    link.is_active = not link.is_active
    db.session.commit()
    return jsonify({"is_active": link.is_active})


@dashboard_bp.route("/links/bulk", methods=["POST"])
@login_required
def bulk_create_links():
    import csv
    import io
    from app.services.link_service import create_short_link
    from app.utils.decorators import check_quota

    if current_user.plan != 'pro':
        flash("Fitur ini hanya untuk pengguna paket Pro.", "danger")
        return redirect(url_for("dashboard.links"))

    file = request.files.get("file")
    if not file or not file.filename.endswith(".csv"):
        flash("Mohon upload file CSV yang valid.", "danger")
        return redirect(url_for("dashboard.links"))

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    
    success_count = 0
    errors = []

    # 1. Handle CSV File
    file = request.files.get("file")
    if file and file.filename.endswith(".csv"):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        for row in reader:
            # Check quota
            result = check_quota(current_user, "links")
            if not result["allowed"]:
                errors.append("Kuota habis.")
                break

            orig = row.get("url", "").strip()
            if not orig: continue
            
            link, err = create_short_link(
                user=current_user,
                original_url=orig,
                custom_alias=row.get("alias", "").strip() or None,
                title=row.get("title", "").strip() or None
            )
            if err: errors.append(f"{orig}: {err}")
            else: success_count += 1

    # 2. Handle Manual Form
    urls    = request.form.getlist("urls[]")
    titles  = request.form.getlist("titles[]")
    aliases = request.form.getlist("aliases[]")

    if urls:
        for i in range(len(urls)):
            # Check quota
            result = check_quota(current_user, "links")
            if not result["allowed"]:
                errors.append("Kuota habis.")
                break

            orig = urls[i].strip()
            if not orig: continue

            link, err = create_short_link(
                user=current_user,
                original_url=orig,
                custom_alias=aliases[i].strip() if i < len(aliases) else None,
                title=titles[i].strip() if i < len(titles) else None
            )
            if err: errors.append(f"{orig}: {err}")
            else: success_count += 1

    if success_count > 0:
        flash(f"Berhasil membuat {success_count} link!", "success")
    if errors:
        flash(f"Ada kendala: {', '.join(errors[:2])}...", "warning")

    return redirect(url_for("dashboard.links"))


# ─── QR Codes ─────────────────────────────────────────────────────────────────

@dashboard_bp.route("/qr")
@login_required
def qr_codes():
    page   = request.args.get("page", 1, type=int)
    query  = current_user.qr_codes.order_by(QRCode.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    return render_template("dashboard/qr_codes.html", pagination=pagination)


@dashboard_bp.route("/qr/create", methods=["POST"])
@login_required
def create_qr():
    from app.services.qr_service import generate_qr_code
    from app.utils.decorators import check_quota

    result = check_quota(current_user, "qrcodes")
    if not result["allowed"]:
        flash(f"Kuota QR bulan ini sudah habis. Upgrade paket Anda.", "danger")
        return redirect(url_for("dashboard.qr_codes"))

    name       = request.form.get("name", "").strip()
    target_url = request.form.get("target_url", "").strip()
    style_config = {
        "dot_style":  request.form.get("dot_style", "square"),
        "fg_color":   request.form.get("fg_color", "#000000"),
        "bg_color":   request.form.get("bg_color", "#FFFFFF"),
    }

    qr, error = generate_qr_code(user=current_user, name=name, target_url=target_url, style_config=style_config)
    if error:
        flash(error, "danger")
    else:
        flash("QR Code berhasil dibuat!", "success")

    return redirect(url_for("dashboard.qr_codes"))


@dashboard_bp.route("/qr/<int:qr_id>/delete", methods=["POST"])
@login_required
def delete_qr(qr_id: int):
    qr = QRCode.query.filter_by(id=qr_id, user_id=current_user.id).first_or_404()
    db.session.delete(qr)
    db.session.commit()
    flash("QR Code dihapus.", "success")
    return redirect(url_for("dashboard.qr_codes"))


# ─── Analytics ────────────────────────────────────────────────────────────────

@dashboard_bp.route("/analytics")
@login_required
def analytics():
    from sqlalchemy import func
    from datetime import timedelta
    import json

    days = 30 if current_user.plan != 'pro' else 365
    cutoff = datetime.utcnow() - timedelta(days=days)

    user_link_ids = [l.id for l in current_user.short_links.all()]

    if not user_link_ids:
        return render_template("dashboard/analytics.html",
            has_data=False, days=days)

    # Klik per hari
    raw_daily = (
        db.session.query(
            func.date(ClickEvent.clicked_at).label("day"),
            func.count().label("cnt")
        )
        .filter(ClickEvent.short_link_id.in_(user_link_ids),
                ClickEvent.clicked_at >= cutoff)
        .group_by(func.date(ClickEvent.clicked_at))
        .order_by(func.date(ClickEvent.clicked_at))
        .all()
    )
    daily_map = {str(r.day): r.cnt for r in raw_daily}
    chart_labels, chart_data = [], []
    for i in range(days - 1, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).date()
        chart_labels.append(d.strftime("%d %b"))
        chart_data.append(daily_map.get(str(d), 0))

    # Device breakdown
    from app.models.click_event import DeviceType
    device_rows = (
        db.session.query(ClickEvent.device_type, func.count().label("cnt"))
        .filter(ClickEvent.short_link_id.in_(user_link_ids),
                ClickEvent.clicked_at >= cutoff)
        .group_by(ClickEvent.device_type)
        .all()
    )
    device_data = {r.device_type.value: r.cnt for r in device_rows}

    # Top 5 links
    top_raw = (
        db.session.query(ShortLink, func.count(ClickEvent.id).label("clicks"))
        .outerjoin(ClickEvent, ClickEvent.short_link_id == ShortLink.id)
        .filter(ShortLink.user_id == current_user.id)
        .group_by(ShortLink.id)
        .order_by(func.count(ClickEvent.id).desc())
        .limit(5)
        .all()
    )
    top_links = [{"slug": r.ShortLink.slug, "url": r.ShortLink.original_url, "clicks": r.clicks} for r in top_raw]
    total_clicks = sum(chart_data)

    return render_template(
        "dashboard/analytics.html",
        has_data=True,
        days=days,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
        device_data=json.dumps(device_data),
        top_links=top_links,
        total_clicks=total_clicks,
    )


@dashboard_bp.route("/links/bulk-template")
@login_required
def download_bulk_template():
    import io
    import csv
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['url', 'title', 'alias'])
    writer.writerow(['https://google.com', 'Google Search', 'google-link'])
    writer.writerow(['https://github.com', 'My Github', 'github-repo'])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=linkcraft_bulk_template.csv"}
    )


# ─── Landing Pages ────────────────────────────────────────────────────────────

@dashboard_bp.route("/pages")
@login_required
def pages():
    from app.models.subscription import PLAN_LIMITS, PlanType

    plan        = current_user.subscription.plan if current_user.subscription else PlanType.free
    limits      = PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.free])
    pages_limit = limits.get("pages_total", 5)
    user_pages  = current_user.landing_pages.order_by(LandingPage.created_at.desc()).all()
    pages_count = len(user_pages)

    return render_template(
        "dashboard/pages.html",
        pages=user_pages,
        pages_count=pages_count,
        pages_limit=pages_limit,
    )


@dashboard_bp.route("/pages/new")
@login_required
def new_page_wizard():
    """Step 1: Select template."""
    from app.models.subscription import PLAN_LIMITS, PlanType
    plan        = current_user.subscription.plan if current_user.subscription else PlanType.free
    limits      = PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.free])
    pages_count = current_user.landing_pages.count()
    if pages_count >= limits["pages_total"]:
        flash(f"Batas halaman tercapai ({pages_count}/{limits['pages_total']}). Upgrade paket Anda.", "danger")
        return redirect(url_for("dashboard.pages"))
    return render_template("dashboard/pages_wizard_template.html",
                           landing_templates=LANDING_TEMPLATES)


@dashboard_bp.route("/pages/configure")
@login_required
def configure_page_wizard():
    """Step 2: Configure slug + preview QR."""
    template_id = request.args.get("template", LANDING_TEMPLATES[0]["id"])
    tmpl = next((t for t in LANDING_TEMPLATES if t["id"] == template_id), LANDING_TEMPLATES[0])
    return render_template("dashboard/pages_wizard_configure.html", tmpl=tmpl)


@dashboard_bp.route("/pages/create", methods=["POST"])
@login_required
def create_page():
    import re
    from app.models.subscription import PLAN_LIMITS, PlanType

    plan   = current_user.subscription.plan if current_user.subscription else PlanType.free
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanType.free])
    pages_count = current_user.landing_pages.count()

    if pages_count >= limits["pages_total"]:
        flash(f"Batas halaman tercapai ({pages_count}/{limits['pages_total']}). Upgrade paket Anda.", "danger")
        return redirect(url_for("dashboard.pages"))

    title       = request.form.get("title", "").strip()
    slug        = request.form.get("slug",  "").strip().lower()
    bio         = request.form.get("bio",   "").strip() or None
    template_id = request.form.get("template_id", LANDING_TEMPLATES[0]["id"])

    if not title or not slug:
        flash("Judul dan slug wajib diisi.", "danger")
        return redirect(url_for("dashboard.configure_page_wizard", template=template_id))

    if not re.match(r'^[a-z0-9][a-z0-9\-]{1,98}[a-z0-9]$', slug):
        flash("Slug hanya boleh berisi huruf kecil, angka, dan tanda hubung (min 3 karakter).", "danger")
        return redirect(url_for("dashboard.configure_page_wizard", template=template_id))

    if LandingPage.query.filter_by(slug=slug).first():
        flash("Slug sudah digunakan. Pilih slug lain.", "danger")
        return redirect(url_for("dashboard.configure_page_wizard", template=template_id))

    tmpl = next((t for t in LANDING_TEMPLATES if t["id"] == template_id), LANDING_TEMPLATES[0])
    page = LandingPage(
        user_id=current_user.id,
        slug=slug,
        title=title,
        bio=bio,
        theme_config={
            "bg_color":    tmpl["bg"],
            "btn_color":   tmpl["btn"],
            "text_color":  tmpl["text"],
            "btn_style":   tmpl["btn_style"],
            "template_id": template_id,
        },
    )
    db.session.add(page)
    db.session.commit()
    return redirect(url_for("dashboard.build_page", page_id=page.id))


@dashboard_bp.route("/pages/<int:page_id>/build", methods=["GET"])
@login_required
def build_page(page_id: int):
    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()
    tab  = request.args.get("tab", "build")
    return render_template("dashboard/pages_build.html", page=page, tab=tab,
                           social_platforms=SOCIAL_PLATFORMS,
                           landing_templates=LANDING_TEMPLATES)


@dashboard_bp.route("/pages/<int:page_id>/design", methods=["POST"])
@login_required
def save_page_design(page_id: int):
    """Save design settings (title, bio, avatar, theme)."""
    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()

    title      = request.form.get("title",      "").strip()
    bio        = request.form.get("bio",        "").strip() or None
    avatar_url = request.form.get("avatar_url", "").strip() or None
    bg_color   = request.form.get("bg_color",   "#0f0f17")
    btn_color  = request.form.get("btn_color",  "#6366f1")
    text_color = request.form.get("text_color", "#e2e8f0")
    btn_style  = request.form.get("btn_style",  "pill")
    template_id = request.form.get("template_id", "")

    if not title:
        flash("Judul wajib diisi.", "danger")
        return redirect(url_for("dashboard.build_page", page_id=page.id, tab="design"))

    page.title      = title
    page.bio        = bio
    page.avatar_url = avatar_url
    page.theme_config = {
        "bg_color":    bg_color,
        "btn_color":   btn_color,
        "text_color":  text_color,
        "btn_style":   btn_style,
        "template_id": template_id,
    }
    db.session.commit()
    flash("Desain berhasil disimpan.", "success")
    return redirect(url_for("dashboard.build_page", page_id=page.id, tab="design"))


# Keep old edit_page route as redirect for backward compat
@dashboard_bp.route("/pages/<int:page_id>/edit", methods=["GET", "POST"])
@login_required
def edit_page(page_id: int):
    if request.method == "POST":
        return save_page_design(page_id)
    return redirect(url_for("dashboard.build_page", page_id=page_id))


@dashboard_bp.route("/pages/<int:page_id>/toggle", methods=["POST"])
@login_required
def toggle_page(page_id: int):
    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()
    page.is_published = not page.is_published
    db.session.commit()
    status = "dipublikasikan" if page.is_published else "disembunyikan"
    flash(f"Halaman berhasil {status}.", "success")
    return redirect(url_for("dashboard.pages"))


@dashboard_bp.route("/pages/<int:page_id>/delete", methods=["POST"])
@login_required
def delete_page(page_id: int):
    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()
    db.session.delete(page)
    db.session.commit()
    flash("Landing page dihapus.", "success")
    return redirect(url_for("dashboard.pages"))


@dashboard_bp.route("/pages/<int:page_id>/links/add", methods=["POST"])
@login_required
def add_page_link(page_id: int):
    from app.models.landing_page import PageLink
    from sqlalchemy import func

    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()

    platform_id = request.form.get("platform", "custom")
    platform    = _PLATFORM_MAP.get(platform_id, _PLATFORM_MAP["custom"])
    icon        = platform["icon"]  # None for custom/shopee/tokopedia
    label = request.form.get("label", "").strip() or platform["label"]
    url   = request.form.get("url",   "").strip()

    if not url:
        flash("URL wajib diisi.", "danger")
        return redirect(url_for("dashboard.build_page", page_id=page.id))

    max_order = db.session.query(func.max(PageLink.sort_order)).filter_by(landing_page_id=page.id).scalar() or 0
    link = PageLink(
        landing_page_id=page.id,
        label=label,
        url=url,
        icon=icon,
        sort_order=max_order + 1,
    )
    db.session.add(link)
    db.session.commit()
    flash("Link berhasil ditambahkan.", "success")
    return redirect(url_for("dashboard.build_page", page_id=page.id))


@dashboard_bp.route("/pages/<int:page_id>/links/<int:link_id>/delete", methods=["POST"])
@login_required
def delete_page_link(page_id: int, link_id: int):
    from app.models.landing_page import PageLink

    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()
    link = PageLink.query.filter_by(id=link_id, landing_page_id=page.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    flash("Link dihapus.", "success")
    return redirect(url_for("dashboard.build_page", page_id=page.id))


@dashboard_bp.route("/pages/<int:page_id>/links/reorder", methods=["POST"])
@login_required
def reorder_page_links(page_id: int):
    from app.models.landing_page import PageLink

    page = LandingPage.query.filter_by(id=page_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    if not data or "order" not in data:
        return jsonify({"error": "Invalid data"}), 400

    for idx, link_id in enumerate(data["order"]):
        PageLink.query.filter_by(id=int(link_id), landing_page_id=page.id).update({"sort_order": idx})
    db.session.commit()
    return jsonify({"ok": True})


@dashboard_bp.route("/pages/check-slug")
@login_required
def check_slug():
    import re
    slug = request.args.get("slug", "").strip().lower()
    if not slug:
        return jsonify({"available": False, "message": "Slug kosong."})
    if not re.match(r'^[a-z0-9][a-z0-9\-]{1,98}[a-z0-9]$', slug):
        return jsonify({"available": False, "message": "Format slug tidak valid."})
    exists = LandingPage.query.filter_by(slug=slug).first()
    if exists:
        return jsonify({"available": False, "message": "Slug sudah digunakan."})
    return jsonify({"available": True})


# ─── Helper ───────────────────────────────────────────────────────────────────

def _get_or_create_quota(user, now):
    from app.models.user import QuotaUsage
    quota = QuotaUsage.query.filter_by(user_id=user.id, year=now.year, month=now.month).first()
    if not quota:
        quota = QuotaUsage(user_id=user.id, year=now.year, month=now.month)
        db.session.add(quota)
        db.session.commit()
    return quota
