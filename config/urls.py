from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Accounts APIs
    path("api/accounts/", include("accounts.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/jobs/", include("jobs.urls"),),
    path("api/applications/", include("applications.urls"),),
    path("api/resumes/", include("resumes.urls")),
    path("api/ai-interviews/", include("ai_interviews.urls")),
    path("api/audit/", include("audit.urls"),),
    path("api/payments/", include("payments.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/admin/billing/", include("subscriptions.admin_billing_urls"),),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
