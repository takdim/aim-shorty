from flask import jsonify, request
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.models import ShortLink


@api_bp.route("/links/check-slug")
@login_required
def check_slug():
    """Check if a custom alias/slug is available."""
    slug = request.args.get("slug", "").strip().lower()
    if not slug:
        return jsonify({"available": False, "message": "Slug tidak boleh kosong."})
    exists = ShortLink.query.filter_by(slug=slug).first()
    return jsonify({"available": not exists})


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
