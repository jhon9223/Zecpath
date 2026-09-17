from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.subscription_service import SubscriptionService


class CurrentSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
