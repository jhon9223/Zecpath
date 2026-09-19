from django.db.models import Sum, Count
from django.utils import timezone

from subscriptions.models import (
    PaymentTransaction,
    UserSubscription,
    BillingHistory,
)


class AdminBillingService:

    @staticmethod
    def transactions():
        return PaymentTransaction.objects.select_related(
            "user",
            "subscription",
            "subscription__plan",
        ).order_by("-created_at")

    @staticmethod
    def subscriptions():
        return UserSubscription.objects.select_related(
            "user",
            "plan",
        ).order_by("-created_at")

    @staticmethod
    def revenue():
        captured = PaymentTransaction.objects.filter(
            status=PaymentTransaction.CAPTURED
        )

        total_revenue = captured.aggregate(
            total=Sum("amount")
        )["total"] or 0

        today = timezone.localdate()

        daily_revenue = captured.filter(
            created_at__date=today
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        monthly_revenue = captured.filter(
            created_at__year=today.year,
            created_at__month=today.month,
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        plan_revenue = captured.values(
            "subscription__plan__name"
        ).annotate(
            revenue=Sum("amount"),
            transactions=Count("id"),
        ).order_by("-revenue")

        return {
            "total_revenue": total_revenue,
            "daily_revenue": daily_revenue,
            "monthly_revenue": monthly_revenue,
            "plan_wise_revenue": list(plan_revenue),
        }

    @staticmethod
    def refunds():
        return BillingHistory.objects.filter(
            event_type=BillingHistory.REFUND
        ).select_related(
            "user",
            "subscription",
            "transaction",
        ).order_by("-created_at")

    @staticmethod
    def failures():
        return PaymentTransaction.objects.filter(
            status=PaymentTransaction.FAILED
        ).select_related(
            "user",
            "subscription",
        ).order_by("-created_at")
