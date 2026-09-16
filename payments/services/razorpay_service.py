import uuid

import razorpay
import hashlib
import hmac


class RazorpayService:

    def __init__(self, key_id=None, key_secret=None):
        self.client = None

        if key_id and key_secret:
            self.client = razorpay.Client(
                auth=(key_id, key_secret)
            )

    def create_order(self, amount, currency="INR", receipt=None):
        amount_in_paise = int(amount * 100)

        if not self.client:
            return {
                "id": f"test_order_{uuid.uuid4().hex[:16]}",
                "amount": amount_in_paise,
                "currency": currency,
                "status": "created",
            }

        data = {
            "amount": amount_in_paise,
            "currency": currency,
        }

        if receipt:
            data["receipt"] = receipt

        return self.client.order.create(data)

    def capture_payment(self, payment_id, amount):
        amount_in_paise = int(amount * 100)

        if not self.client:
            return {
                "id": payment_id,
                "amount": amount_in_paise,
                "status": "captured",
            }

        return self.client.payment.capture(
            payment_id,
            amount_in_paise,
        )

    @staticmethod
    def verify_webhook_signature(payload, signature, secret):
        generated_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            generated_signature,
            signature,
        )
