from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),

    # Accounts APIs
    path("api/accounts/", include("accounts.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/jobs/", include("jobs.urls"),),
    path("api/applications/", include("applications.urls"),),
    path("api/resumes/", include("resumes.urls")),
    path("api/ai-interviews/", include("ai_interviews.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
