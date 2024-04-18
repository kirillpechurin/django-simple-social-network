from rest_framework import filters


class PostCommentOrderingFilter(filters.OrderingFilter):
    ordering_fields = [
        "created_at"
    ]

    def get_default_ordering(self, view):
        return ["-created_at"]
