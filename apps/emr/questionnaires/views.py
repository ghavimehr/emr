from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils.translation import gettext as _
from django.utils import translation

from .forms import get_questionnaire_form
from apps.emr.identity.models import Patient
from .models import Meta


def questionnaire_view(request, lab_testmeta_id):
    """
    Dynamic view for handling a questionnaire.
    """
    # Get the dynamic form class and instructions for the given lab_testmeta_id.
    result = get_questionnaire_form(request, lab_testmeta_id)
    if not result:
        raise Http404(_("Questionnaire not found or not available."))
    DynamicQuestionnaireForm, instructions = result

    if request.method == "POST":
        form = DynamicQuestionnaireForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            # Optionally attach patient information here:
            # record.patient_id = get_object_or_404(Patient, user=request.user)
            record.save()
            return redirect("questionnaire_success")
    else:
        form = DynamicQuestionnaireForm()

    # Retrieve additional Meta data.
    meta_record = get_object_or_404(Meta, lab_testmeta__pk=lab_testmeta_id)
    testmeta_instance = meta_record.lab_testmeta
    questionnaire_name = testmeta_instance.name

    lang_code = translation.get_language_from_request(request)
    current_lang = lang_code.split("-")[0] if lang_code else "en"

    # Dynamically pick the validator for the current language (or empty if not available)
    validator = getattr(meta_record, f"validator_{current_lang}", "") or ""
    reference_article = meta_record.reference_article

    return render(
        request,
        "emr/questionnaires/questionnaire_form.html",
        {
            "form": form,
            "instructions": instructions,
            "questionnaire_name": questionnaire_name,
            "validator": validator,
            "reference_article": reference_article,
        },
    )
