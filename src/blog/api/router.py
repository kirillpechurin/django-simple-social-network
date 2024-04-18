from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns.extend([

    # Posts
    path("posts", viewsets.PostViewSet.as_view({
        "get": "list",
        "post": "create"
    })),

    path("posts/<int:pk>", viewsets.PostViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy"
    })),

    path("posts/<int:pk>/like", viewsets.PostLikeViewSet.as_view({
        "post": "create",
        "delete": "destroy",
    })),

    path("posts/<int:post_id>/comments", viewsets.PostCommentViewSet.as_view({
        "get": "list",
        "post": "create",
    })),

    path("posts/<int:post_id>/comments/<int:pk>", viewsets.PostCommentViewSet.as_view({
        "patch": "update",
        "delete": "destroy",
    })),

    path("blog/users/<int:pk>", viewsets.BlogUserViewSet.as_view({
        "get": "retrieve",
    })),

])
