from django.urls import path
from .views import CurrentSubscriptionAPIView

urlpatterns = [
    path("current/", CurrentSubscriptionAPIView.as_view(),
         name="current-subscription"),
]
