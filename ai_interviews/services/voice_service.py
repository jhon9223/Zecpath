from django.conf import settings
from twilio.rest import Client


class VoiceService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_API_KEY,
            settings.TWILIO_API_SECRET,
            settings.TWILIO_ACCOUNT_SID,
        )

    def make_call(self, to_number):
        call = self.client.calls.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=settings.TWILIO_VOICE_TEMPLATE_URL,
        )

        return call.sid
