"""profiles URL Configuration."""

from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/<str:ens_name>/", views.profile, name="profile"),
]
