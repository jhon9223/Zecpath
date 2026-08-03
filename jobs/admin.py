from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "job_type",
        "status",
        "location",
        "created_at",
    )

    list_filter = (
        "job_type",
        "status",
    )

    search_fields = (
        "title",
        "location",
    )
