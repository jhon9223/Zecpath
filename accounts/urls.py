from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .views import *
urlpatterns = [
    # Signup
    path("signup/", SignupAPIView.as_view(), name="signup"),

    # Login (Generate Access & Refresh Token)
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # Refresh Access Token
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Logout (Blacklist Refresh Token)
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # Profile
    path("profile/", ProfileAPIView.as_view(), name="profile"),

    path("employer/dashboard/", EmployerDashboardAPIView.as_view()),
    path("candidate/dashboard/", CandidateDashboardAPIView.as_view()),
    path("admin/dashboard/", AdminDashboardAPIView.as_view()),
    path("candidate-dashboard/", CandidateDashboardAPIView.as_view(),
         name="candidate-dashboard")
]
