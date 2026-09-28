import json
import uuid

from django.conf import settings
from django.utils import timezone

from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from subscriptions.models import (
    SubscriptionPlan,
    PaymentTransaction,
    BillingHistory,
)

from .models import PaymentWebhookEvent
from .serializers import (
    CreatePaymentOrderSerializer,
    VerifyPaymentSerializer,
    CapturePaymentSerializer,
)
from .services.razorpay_service import RazorpayService


# Swagger documentation serializers
class PaymentDetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class CreatePaymentOrderResponseSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    order_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()


class VerifyPaymentResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    transaction_id = serializers.CharField(required=False)
    order_id = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    status = serializers.CharField(required=False)


class CapturePaymentResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    transaction_id = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    status = serializers.CharField()


class WebhookResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class CreatePaymentOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a payment order",
        description="Create a Razorpay order for an active subscription plan.",
        request=CreatePaymentOrderSerializer,
        responses={
            201: CreatePaymentOrderResponseSerializer,
            404: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description="Subscription plan not found.",
            ),
        },
    )
    def post(self, request):
        serializer = CreatePaymentOrderSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data["plan_id"]

        try:
            plan = SubscriptionPlan.objects.get(
                id=plan_id,
                is_active=True,
            )
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Subscription plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        transaction_id = f"TXN_{uuid.uuid4().hex[:16]}"

        razorpay_service = RazorpayService(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )

        order = razorpay_service.create_order(
            amount=plan.price,
            currency="INR",
            receipt=transaction_id,
        )

        payment_transaction = PaymentTransaction.objects.create(
            user=request.user,
            amount=plan.price,
            currency="INR",
            transaction_id=transaction_id,
            order_id=order["id"],
            status=PaymentTransaction.PENDING,
        )

        return Response(
            {
                "transaction_id": payment_transaction.transaction_id,
                "order_id": order["id"],
                "amount": plan.price,
                "currency": "INR",
                "status": payment_transaction.status,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Verify a payment",
        description=(
            "Verify the Razorpay payment signature for the "
            "authenticated user's transaction."
        ),
        request=VerifyPaymentSerializer,
        responses={
            200: VerifyPaymentResponseSerializer,
            400: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description="Invalid payment signature or request data.",
            ),
            404: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description="Payment transaction not found.",
            ),
        },
    )
    def post(self, request):
        serializer = VerifyPaymentSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        payment_id = serializer.validated_data["payment_id"]
        signature = serializer.validated_data["signature"]

        try:
            transaction = PaymentTransaction.objects.get(
                order_id=order_id,
                user=request.user,
            )
        except PaymentTransaction.DoesNotExist:
            return Response(
                {"detail": "Payment transaction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_valid = RazorpayService.verify_payment_signature(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            secret=settings.RAZORPAY_KEY_SECRET,
        )

        if not is_valid:
            transaction.status = PaymentTransaction.FAILED

            transaction.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return Response(
                {"detail": "Invalid payment signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.payment_id = payment_id
        transaction.status = PaymentTransaction.AUTHORIZED

        transaction.save(
            update_fields=[
                "payment_id",
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "Payment verified successfully.",
                "transaction_id": transaction.transaction_id,
                "order_id": transaction.order_id,
                "payment_id": transaction.payment_id,
                "status": transaction.status,
            },
            status=status.HTTP_200_OK,
        )


class CapturePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Capture a payment",
        description=(
            "Capture an authorized Razorpay payment belonging "
            "to the authenticated user."
        ),
        request=CapturePaymentSerializer,
        responses={
            200: CapturePaymentResponseSerializer,
            400: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description=(
                    "Only authorized payments can be captured "
                    "or request data is invalid."
                ),
            ),
            404: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description="Payment transaction not found.",
            ),
        },
    )
    def post(self, request):
        serializer = CapturePaymentSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        payment_id = serializer.validated_data["payment_id"]

        try:
            transaction = PaymentTransaction.objects.get(
                payment_id=payment_id,
                user=request.user,
            )
        except PaymentTransaction.DoesNotExist:
            return Response(
                {"detail": "Payment transaction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if transaction.status != PaymentTransaction.AUTHORIZED:
            return Response(
                {
                    "detail": (
                        "Only authorized payments can be captured."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        razorpay_service = RazorpayService(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )

        razorpay_service.capture_payment(
            payment_id=payment_id,
            amount=transaction.amount,
        )

        transaction.status = PaymentTransaction.CAPTURED

        transaction.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "Payment captured successfully.",
                "transaction_id": transaction.transaction_id,
                "payment_id": transaction.payment_id,
                "status": transaction.status,
            },
            status=status.HTTP_200_OK,
        )


class RazorpayWebhookAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Receive Razorpay webhook",
        description="Validate and process a Razorpay webhook event.",
        request=None,
        responses={
            200: WebhookResponseSerializer,
            400: OpenApiResponse(
                response=PaymentDetailResponseSerializer,
                description=(
                    "Missing or invalid webhook signature, event ID, "
                    "or JSON payload."
                ),
            ),
        },
    )
    def post(self, request):
        signature = request.headers.get(
            "X-Razorpay-Signature"
        )

        event_id = request.headers.get(
            "x-razorpay-event-id"
        )

        if not signature:
            return Response(
                {"detail": "Missing webhook signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not event_id:
            return Response(
                {"detail": "Missing webhook event ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid = RazorpayService.verify_webhook_signature(
            payload=request.body,
            signature=signature,
            secret=settings.RAZORPAY_WEBHOOK_SECRET,
        )

        if not is_valid:
            return Response(
                {"detail": "Invalid webhook signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return Response(
                {"detail": "Invalid JSON payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = payload.get("event")

        webhook_event, created = (
            PaymentWebhookEvent.objects.get_or_create(
                event_id=event_id,
                defaults={
                    "event_type": event_type or "unknown",
                    "payload": payload,
                },
            )
        )

        if not created and webhook_event.processed:
            return Response(
                {"detail": "Webhook already processed."},
                status=status.HTTP_200_OK,
            )

        self.process_event(
            payload,
            event_type,
        )

        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()

        webhook_event.save(
            update_fields=[
                "processed",
                "processed_at",
            ]
        )

        return Response(
            {
                "detail": "Webhook processed successfully."
            },
            status=status.HTTP_200_OK,
        )

    def process_event(self, payload, event_type):
        if event_type == "payment.authorized":
            self.handle_payment_authorized(payload)

        elif event_type == "payment.captured":
            self.handle_payment_captured(payload)

        elif event_type == "payment.failed":
            self.handle_payment_failed(payload)

        elif event_type.startswith("refund."):
            self.handle_refund(payload)

    def handle_payment_authorized(self, payload):
        payment = payload["payload"]["payment"]["entity"]

        payment_id = payment["id"]
        order_id = payment.get("order_id")

        transaction = PaymentTransaction.objects.filter(
            order_id=order_id
        ).first()

        if transaction:
            transaction.payment_id = payment_id
            transaction.status = PaymentTransaction.AUTHORIZED

            transaction.save(
                update_fields=[
                    "payment_id",
                    "status",
                    "updated_at",
                ]
            )

    def handle_payment_captured(self, payload):
        payment = payload["payload"]["payment"]["entity"]

        payment_id = payment["id"]

        transaction = PaymentTransaction.objects.filter(
            payment_id=payment_id
        ).first()

        if transaction:
            transaction.status = PaymentTransaction.CAPTURED

            transaction.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    def handle_payment_failed(self, payload):
        payment = payload["payload"]["payment"]["entity"]

        payment_id = payment["id"]

        transaction = PaymentTransaction.objects.filter(
            payment_id=payment_id
        ).first()

        if transaction:
            transaction.status = PaymentTransaction.FAILED

            transaction.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    def handle_refund(self, payload):
        refund = payload["payload"]["refund"]["entity"]

        payment_id = refund.get("payment_id")
        refund_amount = refund.get("amount", 0)

        transaction = PaymentTransaction.objects.filter(
            payment_id=payment_id
        ).first()

        if transaction:
            transaction.status = PaymentTransaction.REFUNDED

            transaction.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            BillingHistory.objects.create(
                user=transaction.user,
                subscription=transaction.subscription,
                transaction=transaction,
                event_type=BillingHistory.REFUND,
                amount=refund_amount / 100,
            )
