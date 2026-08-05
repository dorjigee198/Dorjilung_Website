from django.shortcuts import get_object_or_404, redirect, render

from .forms import GrievanceForm
from .models import Grievance


def grievance_form(request):
    if request.method == "POST":
        form = GrievanceForm(request.POST, request.FILES)
        if form.is_valid():
            grievance = form.save()
            return redirect("grievance_submitted", reference_no=grievance.reference_no)
    else:
        form = GrievanceForm()

    return render(request, "grievance/grievance_form.html", {"form": form})


def grievance_submitted(request, reference_no):
    grievance = get_object_or_404(Grievance, reference_no=reference_no)
    return render(
        request,
        "grievance/grievance_submitted.html",
        {"reference_no": grievance.reference_no},
    )
