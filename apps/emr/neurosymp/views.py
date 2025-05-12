# ros/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from apps.emr.identity.models import Patient
from .models import *

from jdatetime import datetime as jdatetime


@login_required(login_url="/users/signin/")
def checkneurosymp_form_view(request):
    # Build categories for the template
    domains = Domain.objects.prefetch_related("neurosymps").all()
    categories = {}
    for dom in domains:
        # Use dom.name directly as the "category" heading
        cat = dom.name
        categories.setdefault(cat, []).append(dom)

    if request.method == "POST":
        patient_id_str = request.POST.get("patient_id", "").strip()
        if not patient_id_str.isdigit():
            messages.error(request, "Please enter a valid numeric Patient ID.")
            return render(request, "emr/ros/ros_form.html", {"categories": categories})

        # Get or create the Patient
        patient_id_int = int(patient_id_str)
        patient, _ = Patient.objects.get_or_create(
            patient_id=patient_id_int, defaults={"name": "Temp", "family_name": "Temp"}
        )

        # Optionally get date + session from the form
        visit_date_str = request.POST.get("visit_date", "")
        session_str = request.POST.get("session_number", "1")

        if visit_date_str:
            try:
                jdt = jdatetime.strptime(visit_date_str, "%Y-%m-%d")
                from datetime import datetime

                visit_date = (
                    jdt.togregorian().date()
                )  # datetime.strptime(visit_date_str, '%Y-%m-%d').date()
            except ValueError:
                visit_date = date.today()
        else:
            visit_date = date.today()

        session_number = int(session_str)

        # Create the new Ros object
        ros_obj = Ros.objects.create(
            patient=patient,
            visit_date=visit_date,
            session_number=session_number,
            data={},
        )

        # Collect each neurosymp's posted status into the Ros.data JSON
        for dom in domains:
            for neurosymp in dom.neurosymps.all():
                posted_status_str = request.POST.get(f"status_{neurosymp.id}", "0")
                ros_obj.data[str(neurosymp.id)] = int(posted_status_str)

        # Save the new data
        ros_obj.save()

        return redirect("ros-success")

    return render(request, "emr/ros/ros_form.html", {"categories": categories})


def ros_success_view(request):
    return render(request, "emr/ros/success.html")
