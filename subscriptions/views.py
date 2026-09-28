
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from drf_spectacular.utils import extend_schema

from .services.subscription_service import SubscriptionService


class SubscriptionFeaturesSerializer(serializers.Serializer):
    paid_job_posting = serializers.BooleanField()
    premium_ai_reports = serializers.BooleanField()
    unlimited_candidates = serializers.BooleanField()


class CurrentSubscriptionResponseSerializer(serializers.Serializer):
    has_active_subscription = serializers.BooleanField()
    plan = serializers.CharField()
    status = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    features = SubscriptionFeaturesSerializer()
    max_job_posts = serializers.IntegerField(required=False)


class CurrentSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current subscription",
        description=(
            "Returns the authenticated user's active subscription, plan, "
            "available features, and job-posting limit. If no active "
            "subscription exists, the FREE plan and its features are returned."
        ),
        responses={
            200: CurrentSubscriptionResponseSerializer,
        },
    )
    def get(self, request):
        subscription = SubscriptionService.get_active_subscription(
            request.user
        )

        if not subscription:
            return Response({
                "has_active_subscription": False,
                "plan": "FREE",
                "features": {
                    "paid_job_posting": False,
                    "premium_ai_reports": False,
                    "unlimited_candidates": False,
                },
            })

        plan = subscription.plan

        return Response({
            "has_active_subscription": True,
            "plan": plan.name,
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "features": {
                "paid_job_posting": SubscriptionService.has_feature(
                    request.user, "paid_job_posting"
                ),
                "premium_ai_reports": SubscriptionService.has_feature(
                    request.user, "premium_ai_reports"
                ),
                "unlimited_candidates": SubscriptionService.has_feature(
                    request.user, "unlimited_candidates"
                ),
            },
            "max_job_posts": plan.max_job_posts,
        })
