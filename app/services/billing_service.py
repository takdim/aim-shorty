import time
from urllib.parse import urlencode

import httpx
import midtransclient
from flask import current_app, url_for

from app.models.app_setting import AppSetting, PaymentGateway
from app.models.subscription import PlanType


class BillingService:
    PLAN_PRICES = {
        PlanType.starter: 50000,
        PlanType.pro: 150000,
    }

    def __init__(self):
        self.gateway = AppSetting.get_payment_gateway()
        self.snap = None
        if self.gateway == PaymentGateway.midtrans:
            self.snap = midtransclient.Snap(
                is_production=current_app.config["MIDTRANS_IS_PRODUCTION"],
                server_key=current_app.config["MIDTRANS_SERVER_KEY"],
                client_key=current_app.config["MIDTRANS_CLIENT_KEY"],
            )

    def create_transaction(self, user, plan_type: PlanType):
        """Create a payment transaction for a plan upgrade based on active gateway."""
        amount = self.PLAN_PRICES.get(plan_type, 0)
        if amount <= 0:
            return None, "Paket tidak valid."

        order_id = self.generate_order_id(user.id, plan_type)
        if self.gateway == PaymentGateway.midtrans:
            return self._create_midtrans_transaction(user, plan_type, amount, order_id)
        if self.gateway == PaymentGateway.doku:
            return None, "Gateway DOKU aktif, tetapi checkout DOKU belum diimplementasikan."
        if self.gateway == PaymentGateway.ipaymu:
            return None, "Gateway iPaymu aktif, tetapi checkout iPaymu belum diimplementasikan."
        if self.gateway == PaymentGateway.pakasir:
            return self._create_pakasir_transaction(plan_type, amount, order_id)

        return None, "Gateway pembayaran tidak dikenali."

    @classmethod
    def generate_order_id(cls, user_id: int, plan_type: PlanType) -> str:
        return f"LC-{user_id}-{plan_type.value}-{int(time.time())}"

    @classmethod
    def get_plan_amount(cls, plan_type: PlanType) -> int:
        return cls.PLAN_PRICES.get(plan_type, 0)

    @classmethod
    def parse_order_id(cls, order_id: str) -> tuple[int, PlanType] | tuple[None, None]:
        parts = (order_id or "").split("-")
        if len(parts) != 4 or parts[0] != "LC":
            return None, None

        try:
            user_id = int(parts[1])
            plan_type = PlanType(parts[2])
        except (TypeError, ValueError):
            return None, None

        return user_id, plan_type

    def verify_pakasir_transaction(self, order_id: str, amount: int):
        params = {
            "project": current_app.config["PAKASIR_PROJECT_SLUG"],
            "amount": amount,
            "order_id": order_id,
            "api_key": current_app.config["PAKASIR_API_KEY"],
        }
        url = f"{current_app.config['PAKASIR_BASE_URL'].rstrip('/')}/api/transactiondetail"

        response = httpx.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        return response.json().get("transaction")

    def _create_midtrans_transaction(self, user, plan_type: PlanType, amount: int, order_id: str):
        param = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": amount,
            },
            "item_details": [{
                "id": plan_type.value,
                "price": amount,
                "quantity": 1,
                "name": f"LinkCraft {plan_type.value.capitalize()} Plan",
            }],
            "customer_details": {
                "first_name": user.name,
                "email": user.email,
            },
            "callbacks": {
                "finish": url_for("billing.finish", _external=True),
            },
        }

        try:
            transaction = self.snap.create_transaction(param)
            transaction["provider"] = PaymentGateway.midtrans.value
            transaction["order_id"] = order_id
            return transaction, None
        except Exception as e:
            current_app.logger.error(f"Midtrans Error: {e}")
            return None, str(e)

    def _create_pakasir_transaction(self, plan_type: PlanType, amount: int, order_id: str):
        project_slug = current_app.config.get("PAKASIR_PROJECT_SLUG")
        if not project_slug:
            return None, "Konfigurasi Pakasir belum lengkap."

        query = urlencode(
            {
                "order_id": order_id,
                "redirect": url_for("billing.finish", _external=True),
            }
        )
        base_url = current_app.config["PAKASIR_BASE_URL"].rstrip("/")
        redirect_url = f"{base_url}/pay/{project_slug}/{amount}?{query}"

        return {
            "provider": PaymentGateway.pakasir.value,
            "order_id": order_id,
            "redirect_url": redirect_url,
            "amount": amount,
            "payment_method": "checkout_redirect",
            "plan": plan_type.value,
        }, None
