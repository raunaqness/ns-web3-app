"""profiles views — ENS search and profile pages."""

from django.shortcuts import render, redirect
from .services import fetch_ens_profile


def home(request):
    """ENS search home page. On GET with ?q=, redirect to the profile page."""
    error = None
    if request.method == "GET" and request.GET.get("q"):
        ens_name = request.GET["q"].strip().lower()
        if not ens_name.endswith(".eth"):
            error = "Please enter a valid .eth name (e.g. vitalik.eth)."
        else:
            return redirect("profiles:profile", ens_name=ens_name)
    return render(request, "profiles/home.html", {"error": error})


def profile(request, ens_name: str):
    """Fetch and display all ENS data for a given ENS name."""
    ens_name = ens_name.strip().lower()
    data = fetch_ens_profile(ens_name)
    print(data)
    # Normalise wallet keys to lowercase so Django template variable lookups work
    # (Django templates treat uppercase dict keys as failed attribute lookups)
    wallets_raw = data.get("wallets", {})
    data["wallets"] = {k.lower(): v for k, v in wallets_raw.items()}

    data["eth"] = data.get("wallets", {}).get("eth")
    data["btc"] = data.get("wallets", {}).get("btc")
    data["sol"] = data.get("wallets", {}).get("sol")

    import json
    print("\n=== ENS PROFILE DATA ===")
    print(json.dumps(data, indent=2, default=str))
    print("========================\n")

    context = {
        "ens_name": ens_name,
        "data": data,
        "error": data.get("error")
    }
    return render(request, "profiles/profile.html", context)
