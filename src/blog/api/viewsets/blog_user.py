from rest_framework import viewsets, permissions

from blog.api.serializers.blog_user import BlogUserSerializer
from users.models import User


class BlogUserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    queryset = User.objects

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BlogUserSerializer
        else:
            raise NotImplementedError
