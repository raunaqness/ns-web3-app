"""core URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda r: HttpResponse("ok")),
    path("", include("profiles.urls")),
]
