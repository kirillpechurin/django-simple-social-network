from rest_framework import permissions


class PostOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.pk == obj.user_id
        return True


class PostNoOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.pk != obj.user_id
