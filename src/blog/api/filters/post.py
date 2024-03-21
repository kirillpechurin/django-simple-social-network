import django_filters
from rest_framework import filters


class PostFilter(django_filters.FilterSet):
    only_from_me = django_filters.BooleanFilter(
        method="filter_by_only_from_me"
    )

    def filter_by_only_from_me(self, queryset, name, value):
        return queryset.filter(
            user_id=self.request.user.pk
        )

    search = django_filters.CharFilter(
        method="filter_by_search"
    )

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            content__icontains=value
        )


class PostOrderingFilter(filters.OrderingFilter):
    ordering_fields = [
        "created_at"
    ]

    def get_default_ordering(self, view):
        return ["-created_at"]
