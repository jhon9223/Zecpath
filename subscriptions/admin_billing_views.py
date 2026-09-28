
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from accounts.permissions import IsAdmin
from .services.billing_service import AdminBillingService


class AdminBillingTransactionsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @extend_schema(
        summary="List admin billing transactions",
        responses={200: OpenApiResponse(
            description="Billing transactions retrieved successfully.")},
    )
    def get(self, request):
        transactions = AdminBillingService.transactions()

        data = []

        for transaction in transactions:
            data.append({
                "id": transaction.id,
                "user": transaction.user.username,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "transaction_id": transaction.transaction_id,
                "order_id": transaction.order_id,
                "payment_id": transaction.payment_id,
                "status": transaction.status,
                "created_at": transaction.created_at,
            })

        return Response(data)


class AdminSubscriptionHistoryAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @extend_schema(
        summary="List admin subscription history",
        responses={200: OpenApiResponse(
            description="Subscription history retrieved successfully.")},
    )
    def get(self, request):
        subscriptions = AdminBillingService.subscriptions()

        data = []

        for subscription in subscriptions:
            data.append({
                "id": subscription.id,
                "user": subscription.user.username,
                "plan": subscription.plan.name,
                "status": subscription.status,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "created_at": subscription.created_at,
            })

        return Response(data)


class AdminRevenueAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @extend_schema(
        summary="Retrieve admin revenue",
        responses={200: OpenApiResponse(
            description="Revenue details retrieved successfully.")},
    )
    def get(self, request):
        return Response(
            AdminBillingService.revenue()
        )


class AdminRefundsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @extend_schema(
        summary="List admin refunds",
        responses={200: OpenApiResponse(
            description="Refunds retrieved successfully.")},
    )
    def get(self, request):
        refunds = AdminBillingService.refunds()

        data = []

        for refund in refunds:
            data.append({
                "id": refund.id,
                "user": refund.user.username,
                "amount": refund.amount,
                "event_type": refund.event_type,
                "transaction_id": (
                    refund.transaction.transaction_id
                    if refund.transaction else None
                ),
                "created_at": refund.created_at,
            })

        return Response(data)


class AdminPaymentFailuresAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    @extend_schema(
        summary="List admin payment failures",
        responses={200: OpenApiResponse(
            description="Payment failures retrieved successfully.")},
    )
    def get(self, request):
        failures = AdminBillingService.failures()

        data = []

        for transaction in failures:
            data.append({
                "id": transaction.id,
                "user": transaction.user.username,
                "amount": transaction.amount,
                "transaction_id": transaction.transaction_id,
                "status": transaction.status,
                "created_at": transaction.created_at,
            })

        return Response(data)
