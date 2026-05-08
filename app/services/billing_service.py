import midtransclient
from flask import current_app, url_for
from app.models.subscription import PlanType

class BillingService:
    def __init__(self):
        self.snap = midtransclient.Snap(
            is_production=current_app.config["MIDTRANS_IS_PRODUCTION"],
            server_key=current_app.config["MIDTRANS_SERVER_KEY"],
            client_key=current_app.config["MIDTRANS_CLIENT_KEY"]
        )

    def create_transaction(self, user, plan_type: PlanType):
        """
        Create a Midtrans Snap transaction for a plan upgrade.
        """
        # Define prices (matching your request)
        prices = {
            PlanType.starter: 50000,
            PlanType.pro: 150000
        }
        
        amount = prices.get(plan_type, 0)
        if amount <= 0:
            return None, "Paket tidak valid."

        order_id = f"ORDER-{user.id}-{int(current_app.config.get('TIMESTAMP', 0)) or 'now'}"
        # We'll use a better order_id in real logic, but for now this is fine
        import time
        order_id = f"LC-{user.id}-{int(time.time())}"

        param = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": amount
            },
            "item_details": [{
                "id": plan_type.value,
                "price": amount,
                "quantity": 1,
                "name": f"LinkCraft {plan_type.value.capitalize()} Plan"
            }],
            "customer_details": {
                "first_name": user.name,
                "email": user.email,
            },
            "callbacks": {
                "finish": url_for('billing.finish', _external=True)
            }
        }

        try:
            transaction = self.snap.create_transaction(param)
            return transaction, None
        except Exception as e:
            current_app.logger.error(f"Midtrans Error: {e}")
            return None, str(e)
