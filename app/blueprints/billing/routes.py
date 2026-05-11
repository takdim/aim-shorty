from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.blueprints.billing import billing_bp
from app.models.subscription import PlanType, SubscriptionStatus
from app.models.app_setting import AppSetting, PaymentGateway
from app.services.billing_service import BillingService
from app.extensions import db
from datetime import datetime

@billing_bp.route("/dashboard/plans")
@login_required
def plans():
    active_gateway = AppSetting.get_payment_gateway()
    return render_template(
        "dashboard/plans.html",
        client_key=current_app.config["MIDTRANS_CLIENT_KEY"],
        payment_gateway=active_gateway.value,
        payment_gateway_label=active_gateway.value.upper() if active_gateway != PaymentGateway.ipaymu else "iPaymu",
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

    # Save transaction info to subscription record (optional but recommended)
    sub = current_user.subscription
    if sub and service.gateway == PaymentGateway.midtrans:
        sub.midtrans_token = transaction['token']
        sub.midtrans_order_id = transaction['redirect_url'].split('=')[-1] # Simple way to get order_id if needed
        db.session.commit()

    return jsonify(transaction)

@billing_bp.route("/billing/finish")
def finish():
    flash("Pembayaran sedang diproses. Mohon tunggu beberapa saat.", "info")
    return redirect(url_for('dashboard.index'))

@billing_bp.route("/billing/webhook", methods=["POST"])
def webhook():
    # TODO: Implement Midtrans Webhook to handle async payment success
    # This will be called by Midtrans servers
    data = request.json
    current_app.logger.info(f"Midtrans Webhook Received: {data}")
    return jsonify({"status": "ok"})
