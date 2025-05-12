# ros/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime
from django.utils.translation import gettext as _
import pytz

from apps.emr.identity.models import Patient
from .models import *
from jdatetime import datetime as jdatetime


@login_required(login_url="/users/signin/")
def ros_form_view(request):
    # Fetch all systems for displaying
    systems = System.objects.prefetch_related("symptoms").all()
    categories = {}
    for sys in systems:
        cat = sys.name
        categories.setdefault(cat, []).append(sys)

    selected_patient_id = request.session.get("selected_patient_id")
    if not selected_patient_id:
        messages.error(
            request, "No patient is currently selected. Please select a patient first."
        )
        # re-render the same page or redirect to a patient selection page
        return render(request, "emr/ros/ros_form.html", {"categories": categories})

    try:
        patient = Patient.objects.get(id=selected_patient_id)
    except Patient.DoesNotExist:
        messages.error(
            request,
            _("The selected patient no longer exists. Please select another patient."),
        )
        return render(request, "emr/ros/ros_form.html", {"categories": categories})

    if request.method == "POST":
        # 1. Get the posted Jalali date string
        visit_date_str = request.POST.get("visit_date", "").strip()
        session_str = request.POST.get("session_number", "1").strip()

        # 2. Convert Jalali date to Gregorian if provided, else use "today" in Tehran time
        if visit_date_str:
            try:
                # Example format: "1402-10-15"
                jdt = jdatetime.strptime(visit_date_str, "%Y-%m-%d")
                visit_date = jdt.togregorian().date()
            except ValueError:
                messages.error(
                    request, "Invalid Jalali date. Using today's Tehran date instead."
                )
                visit_date = _tehran_date_today()
        else:
            # If no date is provided, default to today's date in Tehran
            visit_date = _tehran_date_today()

        # Session number
        session_number = 1
        if session_str.isdigit():
            session_number = int(session_str)

        # Create new Ros object
        ros_obj = Ros.objects.create(
            patient=patient,
            visit_date=visit_date,
            session_number=session_number,
            data={},
        )

        # For each symptom, store posted status
        for sys in systems:
            for symptom in sys.symptoms.all():
                posted_status_str = request.POST.get(f"status_{symptom.id}", "0")
                ros_obj.data[str(symptom.id)] = int(posted_status_str)

        ros_obj.save()

        # Instead of redirect, show a success message and re-render the page
        messages.success(request, _("ROS data successfully submitted."))

        # If you want to "reset" the form fields, you can skip re-populating data
        # or if you want the user to see the same data, you can do so as well
        return render(
            request,
            "emr/ros/ros_form.html",
            {
                "categories": categories,
                # optionally pass data for re-display
                "visit_date": visit_date_str,
                "session_number": session_number,
            },
        )
    context = {
        "segment": "ros",
        "parent": "physician",
        "page_title": _("Review of Systems"),
        "categories": categories,
    }
    # GET request: just show the form without submission
    return render(request, "emr/ros/ros_form.html", context)


def _tehran_date_today():
    """
    Returns today's date in the Asia/Tehran time zone as a Python date object.
    """
    import pytz

    tehran_tz = pytz.timezone("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)  # current local dt
    return now_tehran.date()
