from django.shortcuts import render

from .models import CLDPActivity, CLDPSettings, cldp_dashboard_stats


def cldp_dashboard(request):
    activities = CLDPActivity.objects.prefetch_related("images__image")
    settings = CLDPSettings.load(request_or_site=request)

    context = {
        "intro_text": settings.intro_text,
        "activities": activities,
        "stats": cldp_dashboard_stats(activities),
    }
    return render(request, "cldp/cldp_dashboard.html", context)
