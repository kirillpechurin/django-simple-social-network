from rest_framework import permissions


class PostNoOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.pk != view.get_post().user_id
        return True


class PostCommentOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.pk == obj.user_id
        return True
