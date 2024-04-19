import django_filters
from django.db import models
from rest_framework import filters
from common.api import filters as custom_filters

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


class PostOrderingFilter(custom_filters.OrderingFilter):
    ordering_param_field_map = {
        "created_at": "created_at",
        "from_subscriptions": "from_subscriptions"
    }

    additional_ordering = (
        "-created_at",
    )

    def get_default_ordering(self, view):
        return ["from_subscriptions", "-created_at"]

    def _get_queryset(self, request, queryset, ordering):
        if "from_subscriptions" in self._used:
            queryset = queryset.annotate(
                from_subscriptions=models.Case(
                    models.When(
                        models.Q(user__subscribers__user_id=request.user.pk),
                        then=models.Value(1)
                    ),
                    default=models.Value(0),
                    output_field=models.IntegerField()
                )
            )
        return queryset
