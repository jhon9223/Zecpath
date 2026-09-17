from rest_framework.permissions import BasePermission
from subscriptions.services.subscription_service import SubscriptionService


class PremiumAIAccessPermission(BasePermission):
    message = "Premium AI reports require an active paid subscription."

    def has_permission(self, request, view):
        return SubscriptionService.has_feature(
            request.user,
            "premium_ai_reports",
        )


class PaidJobPostingPermission(BasePermission):
    message = "Paid job posting requires an active PRO or ENTERPRISE subscription."

    def has_permission(self, request, view):
        return SubscriptionService.has_feature(
            request.user,
            "paid_job_posting",
        )


class UnlimitedCandidateAccessPermission(BasePermission):
    message = "Unlimited candidate access requires an ENTERPRISE subscription."

    def has_permission(self, request, view):
        return SubscriptionService.has_feature(
            request.user,
            "unlimited_candidates",
        )
