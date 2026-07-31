import django_filters

from .models import CandidateProfile


class CandidateProfileFilter(django_filters.FilterSet):

    username = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains"
    )

    created_after = django_filters.DateFilter(
        field_name="user__created_at",
        lookup_expr="gte"
    )

    created_before = django_filters.DateFilter(
        field_name="user__created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = CandidateProfile
        fields = [
            "is_deleted",
            "username",
            "created_after",
            "created_before",
        ]
