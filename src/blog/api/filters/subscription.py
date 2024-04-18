import django_filters
from rest_framework import filters


def _set_default(data, key, value):
    if data is not None:
        data = data.copy()
        if not data.get(key):
            data[key] = value
    return data


class SubscriptionFilter(django_filters.FilterSet):

    def __init__(self, data=None, *args, **kwargs):
        data = _set_default(data, "user_id", kwargs["request"].user.pk)
        super().__init__(data, *args, **kwargs)

    user_id = django_filters.NumberFilter(
        method="filter_by_user_id"
    )

    def filter_by_user_id(self, queryset, name, value):
        return queryset.filter(
            user_id=value
        )

    search = django_filters.CharFilter(
        method="filter_by_search"
    )

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            to_user__username=value
        )


class SubscriptionOrderingFilter(filters.OrderingFilter):
    ordering_fields = [
        "created_at"
    ]

    def get_default_ordering(self, view):
        return ["-created_at"]


class SubscriberFilter(django_filters.FilterSet):

    def __init__(self, data=None, *args, **kwargs):
        data = _set_default(data, "to_user_id", kwargs["request"].user.pk)
        super().__init__(data, *args, **kwargs)

    to_user_id = django_filters.NumberFilter(
        method="filter_by_to_user_id"
    )

    def filter_by_to_user_id(self, queryset, name, value):
        return queryset.filter(
            to_user_id=value
        )

    search = django_filters.CharFilter(
        method="filter_by_search"
    )

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            user__username=value
        )


class SubscriberOrderingFilter(SubscriptionOrderingFilter):
    pass
