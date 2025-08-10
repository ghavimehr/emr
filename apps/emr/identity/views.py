from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, FileResponse
from django.utils.translation import gettext as _
from django_jalali.templatetags.jformat import jformat
from django.utils.translation import activate
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
import logging
import json
import datetime, jwt


from .models import *
from .forms import IdentityForm
from .utils import agreement_generator
from apps.emr.events.models import Event
from django.conf import settings
from apps.emr.files.views import serve_patient_file

logger = logging.getLogger("django")


@staff_member_required(login_url='/users/signin/')
def identity_list(request):
    # 1) Base queryset
    qs = Patient.objects.all()

    # 2) Read search parameters from GET
    patient_id = request.GET.get("patient_id", "").strip()
    first_name = request.GET.get("first_name", "").strip()
    last_name = request.GET.get("last_name", "").strip()
    ssn = request.GET.get("ssn", "").strip()
    gender_id = request.GET.get("gender", "").strip()
    dominanthand_id = request.GET.get("dominanthand", "").strip()
    insurance_id = request.GET.get("insurance", "").strip()

    # 3) Filter as needed
    if patient_id:
        qs = qs.filter(patient_id__exact=patient_id)

    if first_name:
        qs = qs.filter(first_name__icontains=first_name)

    if last_name:
        qs = qs.filter(last_name__icontains=last_name)

    if ssn:
        qs = qs.filter(ssn__exact=ssn)

    if gender_id:
        qs = qs.filter(gender_id=gender_id)

    if dominanthand_id:
        qs = qs.filter(dominanthand_id=dominanthand_id)

    if insurance_id:
        qs = qs.filter(insurances__id=insurance_id)

    # 4) Annotate with latest event date and time based on the Event model.
    latest_event_date = Subquery(
        Event.objects.filter(patient_id=OuterRef("id"))
        .order_by("-date", "-time")
        .values("date")[:1]
    )
    latest_event_time = Subquery(
        Event.objects.filter(patient_id=OuterRef("id"))
        .order_by("-date", "-time")
        .values("time")[:1]
    )

    qs = qs.annotate(
        latest_event_date=latest_event_date,
        latest_event_time=latest_event_time,
    ).order_by("-latest_event_date", "-latest_event_time")

    # 5) Pagination logic
    try:
        rows_per_page = int(request.GET.get("rows", 10))
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(qs, rows_per_page)
    page_number = request.GET.get("page")
    identities = paginator.get_page(page_number)

    # 6) For building select dropdowns in the advanced search, pass model data:
    all_genders = Gender.objects.all()
    all_dominant_hands = DominantHand.objects.all()
    all_insurances = Insurance.objects.all()

    context = {
        "identities": identities,
        "all_genders": all_genders,
        "all_dominant_hands": all_dominant_hands,
        "all_insurances": all_insurances,
    }
    return render(request, "emr/identity/identity_list.html", context)


@staff_member_required(login_url='/users/signin/')
def identity_create(request):
    if request.method == "POST":
        if "save_and_add" in request.POST:
            # user clicked "Save and Add Another"
            form = IdentityForm(request.POST, request=request)
            if form.is_valid():
                new_patient = form.save()
                form.save_m2m()
                # store new patient in session
                request.session["selected_patient_id"] = new_patient.id
                messages.success(request, "Patient created successfully.")
                logger.debug(
                    f"Creating PDF for new patient: {new_patient.first_name} {new_patient.last_name}"
                )
                # Redirect to create again (empty form)
                return redirect("identity-create")
            else:
                messages.error(request, "Error. Please correct the form.")
        else:
            # normal save
            form = IdentityForm(request.POST, request=request)
            if form.is_valid():
                new_patient = form.save()
                # store new patient in session
                request.session["selected_patient_id"] = new_patient.id
                messages.success(request, "Patient created successfully.")
                return redirect("identity-list")
            else:
                messages.error(request, "Error. Please correct the form.")
    else:
        form = IdentityForm(request=request)

    context = {
        "form": form,
        "form_title": _("Create a New Patient"),
        "segment": "identity_create",
        "parent": "identity",
        "page_title": _("Create a New Patient"),
        "formatted_birthday": (
            jformat(form.instance.birthday, "Y/m/d") if form.instance.birthday else None
        ),
    }

    return render(request, "emr/identity/identity_form.html", context)


@staff_member_required(login_url='/users/signin/')
def identity_update(request, pk):
    identity_obj = get_object_or_404(Patient, pk=pk)

    if request.method == "POST":
        if "start_edit" in request.POST:
            # just clicked "Start Edit" => do nothing but re-render the same form in edit mode
            pass
        elif "saveSubmitButton" in request.POST:
            form = IdentityForm(request.POST, instance=identity_obj, request=request)
            if form.is_valid():
                updated_patient = form.save()
                form.save_m2m()
                request.session["selected_patient_id"] = updated_patient.id
                messages.success(request, _("Patient updated successfully."))
                return redirect("identity-list")
            else:
                messages.error(request, _("Error updating patient."))
        else:
            # Some other button?
            pass

    # GET or no relevant POST
    # By default, show read-only unless "start_edit" was posted or patient is new
    read_only = True
    form = IdentityForm(instance=identity_obj, request=request)
    if request.method == "POST" and "start_edit" in request.POST:
        read_only = False

    context = {
        "form": form,
        "form_title": _("Edit Patient"),
        "segment": "identity_update",
        "parent": "identity",
        "page_title": _("Update a Patient"),
        "read_only": read_only,
        "identity_obj": identity_obj,
        "formatted_birthday": (
            jformat(form.instance.birthday, "Y/m/d") if form.instance.birthday else None
        ),
    }

    return render(request, "emr/identity/identity_form.html", context)


@staff_member_required(login_url='/users/signin/')
def identity_delete(request, pk):
    identity_obj = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        identity_obj.delete()
        return redirect("identity-list")

    return render(
        request, "emr/identity/identity_confirm_delete.html", {"identity": identity_obj}
    )


@staff_member_required(login_url='/users/signin/')
def occupation_search(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 3:
        return JsonResponse([], safe=False)

    # search existing
    results = Occupation.objects.filter(name__icontains=query)[:10]
    data = [{"id": o.id, "name": o.name} for o in results]
    return JsonResponse(data, safe=False)


@staff_member_required(login_url='/users/signin/')
def Secretarytags_search(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 3:
        return JsonResponse([], safe=False)
    matches = Secretarytags.objects.filter(name__icontains=q)[:10]
    data = [{"id": st.id, "name": st.name} for st in matches]
    return JsonResponse(data, safe=False)


@staff_member_required(login_url='/users/signin/')
def Secretarytags_add(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tag_name = data.get("name", "").strip()
        if tag_name:
            tag, created = Secretarytags.objects.get_or_create(name=tag_name)
            return JsonResponse({"id": tag.id, "name": tag.name}, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)


@staff_member_required(login_url='/users/signin/')
def agreement(request, patient_id):
    # Call the demographic_report function
    message, new_doc = agreement_generator(patient_id)

    # reference_number = Patient.objects.values_list("patient_id", flat=True).get(id=patient_id)
    hex_key = new_doc.id.hex  # e.g. "55d4d68a72ff465e939b296b1f879f44"

    now = datetime.datetime.utcnow()
    payload = {
        "key": hex_key,               # must match serve_patient_file’s `payload["key"]`
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.ONLYOFFICE_JWT_SECRET, algorithm="HS256")


    return JsonResponse({
        "key":   str(new_doc.id),
        "token": token,
    })
    # 3) inject the Authorization header into this request
    # request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    # return serve_patient_file(request, key=str(new_doc.id))


    # 4) hand off directly to serve_patient_file
    #    it will run your IP‐allow logic, JWT decode, lookup by id=new_doc.id, and stream.

    # if pdf_path:
    #     # If report was generated successfully, return the PDF file as response
    #     response = FileResponse(open(pdf_path, "rb"), content_type="application/pdf")
    #     response["Content-Disposition"] = (
    #         f'attachment; filename="commitment_letter_{reference_number}.pdf"'
    #     )
    #     return response
    # else:
    #     # If there was an error, show the error message
    #     messages.error(request, message)
    #     return redirect(
    #         "identity-list"
    #     )  # Redirect to the patient list if there is an error
