from datetime import datetime, timedelta

import httpx
from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.blueprints.billing import billing_bp
from app.extensions import csrf, db
from app.models.app_setting import AppSetting, PaymentGateway
from app.models.subscription import PlanType, SubscriptionStatus
from app.models.user import User
from app.services.billing_service import BillingService


@billing_bp.route("/dashboard/plans")
@login_required
def plans():
    active_gateway = AppSetting.get_payment_gateway()
    return render_template(
        "dashboard/plans.html",
        client_key=current_app.config["MIDTRANS_CLIENT_KEY"],
        payment_gateway=active_gateway.value,
        payment_gateway_label=active_gateway.label,
    )


@billing_bp.route("/dashboard/checkout/<plan_name>", methods=["POST"])
@login_required
def checkout(plan_name):
    try:
        plan_type = PlanType(plan_name)
    except ValueError:
        return jsonify({"error": "Paket tidak valid"}), 400

    service = BillingService()
    transaction, error = service.create_transaction(current_user, plan_type)

    if error:
        return jsonify({"error": error, "provider": service.gateway.value}), 400

    sub = current_user.subscription
    if sub and service.gateway == PaymentGateway.midtrans:
        sub.midtrans_token = transaction["token"]
        sub.midtrans_order_id = transaction["order_id"]
        db.session.commit()

    return jsonify(transaction)


@billing_bp.route("/billing/finish")
def finish():
    flash("Pembayaran sedang diproses. Mohon tunggu beberapa saat.", "info")
    return redirect(url_for("dashboard.index"))


@billing_bp.route("/billing/webhook", methods=["POST"])
@csrf.exempt
def webhook():
    data = request.get_json(silent=True) or {}
    current_app.logger.info("Billing webhook received: %s", data)

    project = data.get("project")
    order_id = data.get("order_id")
    status = (data.get("status") or "").lower()
    amount = data.get("amount")

    if project == current_app.config.get("PAKASIR_PROJECT_SLUG"):
        return _handle_pakasir_webhook(order_id, amount, status)

    return jsonify({"status": "ignored"}), 200


def _handle_pakasir_webhook(order_id: str, amount, status: str):
    if not order_id or amount is None:
        return jsonify({"error": "Payload webhook Pakasir tidak lengkap."}), 400

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Amount webhook Pakasir tidak valid."}), 400

    if status != "completed":
        return jsonify({"status": "ignored"}), 200

    service = BillingService()
    try:
        transaction = service.verify_pakasir_transaction(order_id, amount)
    except httpx.HTTPError as exc:
        current_app.logger.error("Pakasir verification failed for %s: %s", order_id, exc)
        return jsonify({"error": "Gagal verifikasi transaksi Pakasir."}), 502

    if not transaction:
        return jsonify({"error": "Transaksi Pakasir tidak ditemukan."}), 404
    if transaction.get("status") != "completed":
        return jsonify({"status": "ignored"}), 200

    applied, message = _apply_paid_subscription(order_id, amount)
    if not applied:
        return jsonify({"error": message}), 400

    return jsonify({"status": "ok"}), 200


def _apply_paid_subscription(order_id: str, amount: int):
    user_id, plan_type = BillingService.parse_order_id(order_id)
    if user_id is None or plan_type is None:
        return False, "Format order ID tidak dikenali."

    expected_amount = BillingService.get_plan_amount(plan_type)
    if amount != expected_amount:
        return False, "Nominal transaksi tidak sesuai paket."

    user = db.session.get(User, user_id)
    if not user or not user.subscription:
        return False, "User atau subscription tidak ditemukan."

    subscription = user.subscription
    if subscription.plan == plan_type and subscription.status == SubscriptionStatus.active:
        if subscription.current_period_end and subscription.current_period_end > datetime.utcnow():
            return True, "Subscription sudah aktif."

    now = datetime.utcnow()
    subscription.plan = plan_type
    subscription.status = SubscriptionStatus.active
    subscription.current_period_start = now
    subscription.current_period_end = now + timedelta(days=30)
    subscription.cancelled_at = None
    db.session.commit()

    return True, "Subscription berhasil diaktifkan."
