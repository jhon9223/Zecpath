from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .views import SignupAPIView, LogoutAPIView, ProfileAPIView
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


]
