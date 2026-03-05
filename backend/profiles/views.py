"""profiles views — placeholder stubs for Task 1.3 & 1.4."""

from django.shortcuts import render


def home(request):
    """ENS search home page."""
    return render(request, "profiles/home.html")


def profile(request, ens_name: str):
    """ENS profile page for a given ENS name."""
    context = {"ens_name": ens_name}
    return render(request, "profiles/profile.html", context)
