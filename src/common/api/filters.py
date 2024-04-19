from typing import Optional, Dict, Tuple

from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    ordering_param_field_map: Optional[Dict] = None

    additional_ordering: Optional[Tuple[str]] = None

    def __init__(self):
        assert self.ordering_param_field_map is not None

        self.ordering_fields = list(self.ordering_param_field_map.keys())
        self._used = set()

    def _get_additional_ordering(self, ordering):
        if not self.additional_ordering:
            return ordering

        for ordering_param in self.additional_ordering:
            if (
                    ordering_param.startswith("-") and
                    ordering_param in ordering
            ) or (
                    f"-{ordering_param}" in ordering
            ):
                continue
            ordering.append(ordering_param)
        return ordering

    def _to_fields(self, ordering):
        for i in range(0, len(ordering)):
            desc = ordering[i].startswith("-")
            if field := self.ordering_param_field_map.get(ordering[i][1:] if desc else ordering[i]):
                ordering[i] = f"-{field}" if desc else field
                self._used.add(field)
        return ordering

    def _get_queryset(self, request, queryset, ordering):
        return queryset

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        ordering = self._get_additional_ordering(ordering)
        if ordering:
            ordering = self._to_fields(ordering)
            queryset = self._get_queryset(request, queryset, ordering)
            return queryset.order_by(*ordering)

        return queryset
