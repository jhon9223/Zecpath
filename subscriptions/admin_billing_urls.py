from django.urls import path

from .admin_billing_views import (
    AdminBillingTransactionsAPIView,
    AdminSubscriptionHistoryAPIView,
    AdminRevenueAPIView,
    AdminRefundsAPIView,
    AdminPaymentFailuresAPIView,
)

urlpatterns = [
    path(
        "transactions/",
        AdminBillingTransactionsAPIView.as_view(),
    ),
    path(
        "subscriptions/",
        AdminSubscriptionHistoryAPIView.as_view(),
    ),
    path(
        "revenue/",
        AdminRevenueAPIView.as_view(),
    ),
    path(
        "refunds/",
        AdminRefundsAPIView.as_view(),
    ),
    path(
        "failures/",
        AdminPaymentFailuresAPIView.as_view(),
    ),
]
