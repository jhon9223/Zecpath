from django.urls import path

from .views import (
    CreatePaymentOrderAPIView,
    VerifyPaymentAPIView,
    CapturePaymentAPIView,
    RazorpayWebhookAPIView,
)


urlpatterns = [
    path(
        "orders/",
        CreatePaymentOrderAPIView.as_view(),
        name="create-payment-order",
    ),
    path(
        "verify/",
        VerifyPaymentAPIView.as_view(),
        name="verify-payment",
    ),
    path(
        "capture/",
        CapturePaymentAPIView.as_view(),
        name="capture-payment",
    ),
    path(
        "webhook/",
        RazorpayWebhookAPIView.as_view(),
        name="razorpay-webhook",
    ),
]
