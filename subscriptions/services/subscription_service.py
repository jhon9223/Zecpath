from django.utils import timezone
from subscriptions.models import UserSubscription


class SubscriptionService:

    @staticmethod
    def get_active_subscription(user):
        subscription = (
            UserSubscription.objects
            .filter(user=user, status=UserSubscription.ACTIVE)
            .select_related("plan")
            .order_by("-end_date")
            .first()
        )

        if not subscription:
            return None

        if subscription.end_date <= timezone.now():
            subscription.status = UserSubscription.EXPIRED
            subscription.save(update_fields=["status"])
            return None

        return subscription

    @staticmethod
    def has_feature(user, feature):
        subscription = SubscriptionService.get_active_subscription(user)

        if not subscription:
            return False

        plan = subscription.plan

        if feature == "premium_ai_reports":
            return plan.ai_analytics

        if feature == "advanced_analytics":
            return plan.advanced_analytics

        if feature == "unlimited_candidates":
            return plan.name == UserSubscription.plan.field.related_model.ENTERPRISE

        if feature == "paid_job_posting":
            return plan.name in ["PRO", "ENTERPRISE"]

        return False

    @staticmethod
    def can_create_job(user, current_job_count):
        subscription = SubscriptionService.get_active_subscription(user)

        if not subscription:
            return current_job_count < 1

        max_jobs = subscription.plan.max_job_posts

        if max_jobs is None:
            return True

        return current_job_count < max_jobs
