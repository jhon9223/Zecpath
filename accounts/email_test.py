from django.core.mail import send_mail


def send_test_email():
    send_mail(
        subject="Zecpath Test Email",
        message="Hello! This is a test email from Zecpath.",
        from_email="noreply@zecpath.com",
        recipient_list=["test@example.com"],
    )
