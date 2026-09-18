from rest_framework.throttling import UserRateThrottle


class PremiumFeatureThrottle(UserRateThrottle):
    scope = "premium_feature"
