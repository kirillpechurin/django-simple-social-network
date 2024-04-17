from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/v1/", include("users.api.router")),
    path("api/v1/", include("blog.api.router")),
    path("api/v1/", include("notifications.api.router")),
]
