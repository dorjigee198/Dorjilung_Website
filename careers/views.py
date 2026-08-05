from django.db.models import Q
from django.shortcuts import render

from .models import STATUS_OPEN, JobOpening


def careers_list(request):
    query = request.GET.get("q", "").strip()
    jobs_qs = JobOpening.objects.prefetch_related("documents__document")
    if query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query) | Q(department__icontains=query)
        )
    jobs = list(jobs_qs)

    open_jobs = sorted(
        (j for j in jobs if j.computed_status == STATUS_OPEN),
        key=lambda j: j.closing_date,
    )
    other_jobs = sorted(
        (j for j in jobs if j.computed_status != STATUS_OPEN),
        key=lambda j: j.closing_date,
        reverse=True,
    )

    context = {
        "open_jobs": open_jobs,
        "other_jobs": other_jobs,
        "query": query,
    }
    return render(request, "careers/careers_list.html", context)
