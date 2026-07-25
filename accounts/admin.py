from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, EmployerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "phone",
                    "role",
                    "is_verified",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


admin.site.register(CandidateProfile)
admin.site.register(EmployerProfile)
