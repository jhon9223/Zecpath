import hashlib
import hmac


secret = "test_webhook_secret"

raw_body = b'{"event":"refund.created","payload":{"refund":{"entity":{"id":"rfnd_test_123","payment_id":"pay_test_123","amount":99900}}}}'

signature = hmac.new(
    secret.encode(),
    raw_body,
    hashlib.sha256,
).hexdigest()

print(signature)
