from flask import render_template, redirect, url_for, request, flash, session
from app.blueprints.public import public_bp
from app.extensions import db
from app.models import ShortLink, ClickEvent, LandingPage
from app.models.click_event import ClickSourceType


@public_bp.route("/")
def index():
    return render_template("public/index.html")


@public_bp.route("/<slug>")
def redirect_short_link(slug: str):
    link = ShortLink.query.filter_by(slug=slug, is_active=True).first_or_404()

    if link.is_expired:
        flash("Link ini sudah kedaluwarsa.", "warning")
        return redirect(url_for("public.index"))

    # Log click event
    from app.services.analytics_service import log_click
    log_click(
        source_type=ClickSourceType.short_link,
        short_link_id=link.id,
        request=request,
    )

    # ── Interstitial Ad for Free plan owners ─────────────────────────────────
    owner = link.user
    if owner and owner.plan == "free":
        return render_template(
            "public/interstitial.html",
            link=link,
            destination=link.original_url,
            countdown=7,
        )

    return redirect(link.original_url, code=302)


@public_bp.route("/p/<slug>")
def landing_page(slug: str):
    page = LandingPage.query.filter_by(slug=slug, is_published=True).first_or_404()

    # Log view event
    from app.services.analytics_service import log_click
    log_click(
        source_type=ClickSourceType.landing_page,
        landing_page_id=page.id,
        request=request,
    )

    return render_template("public/landing_page.html", page=page)
