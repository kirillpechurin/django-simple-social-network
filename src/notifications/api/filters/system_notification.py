import django_filters
from rest_framework import filters


class SystemNotificationFilter(django_filters.FilterSet):
    type_id = django_filters.NumberFilter(
        method="filter_by_type_id"
    )

    def filter_by_type_id(self, queryset, name, value):
        return queryset.filter(
            type_id=value
        )


class SystemNotificationOrderingFilter(filters.OrderingFilter):
    ordering_fields = [
        "created_at"
    ]

    def get_default_ordering(self, view):
        return ["-created_at"]
