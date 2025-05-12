from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext as _
import logging

from .models import RTMS
from apps.emr.events.models import Event

logger = logging.getLogger("django")


@login_required(login_url="/users/signin/")
def rtms_overview(request):
    # 1) Base queryset for rTMS records
    qs = RTMS.objects.all()

    # 2) Read search parameters from GET
    patient_id = request.GET.get("patient_id", "").strip()
    pulse_type = request.GET.get("pulse_type", "").strip()
    unknown_variable_1 = request.GET.get("unknown_variable_1", "").strip()
    unknown_variable_2 = request.GET.get("unknown_variable_2", "").strip()
    total_sessions = request.GET.get("total_sessions", "").strip()
    total_pulse = request.GET.get("total_pulse", "").strip()

    # 3) Apply filters if provided
    if patient_id:
        qs = qs.filter(identity_patient__patient_id__icontains=patient_id)
    if pulse_type:
        qs = qs.filter(pulse_type__name__icontains=pulse_type)
    if unknown_variable_1:
        qs = qs.filter(unknown_variable_1=unknown_variable_1)
    if unknown_variable_2:
        qs = qs.filter(unknown_variable_2=unknown_variable_2)
    if total_sessions:
        qs = qs.filter(total_sessions=total_sessions)
    if total_pulse:
        qs = qs.filter(total_pulse=total_pulse)

    # 4) Annotate with latest event date and time based on the Event model,
    # using the patient linked to each rTMS record
    latest_event_date = Subquery(
        Event.objects.filter(patient_id=OuterRef("identity_patient_id"))
        .order_by("-date", "-time")
        .values("date")[:1]
    )
    latest_event_time = Subquery(
        Event.objects.filter(patient_id=OuterRef("identity_patient_id"))
        .order_by("-date", "-time")
        .values("time")[:1]
    )
    qs = qs.annotate(
        latest_event_date=latest_event_date,
        latest_event_time=latest_event_time,
    ).order_by("-latest_event_date", "-latest_event_time")

    # 5) Apply pagination logic
    try:
        rows_per_page = int(request.GET.get("rows", 10))
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(qs, rows_per_page)
    page_number = request.GET.get("page")
    rtms_list = paginator.get_page(page_number)

    context = {
        "rtms_list": rtms_list,
        "search_params": request.GET,
    }
    return render(request, "emr/rtms/rtms_overview.html", context)
