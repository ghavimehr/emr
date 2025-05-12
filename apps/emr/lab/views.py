from django.utils.translation import get_language
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from apps.emr.identity.models import Patient
from django.utils.translation import gettext as _
from .utils import get_tests_for_category
from .forms import get_lab_forms_for_category
import logging

from .models import Category

logger = logging.getLogger(__name__)


def lab_category_view(request, category_name):
    logger.info(f"lab_category_view called for category: {category_name}")

    # Retrieve the selected patient from session.
    selected_patient_id = request.session.get("selected_patient_id")
    if not selected_patient_id:
        messages.error(
            request, _("No patient selected. Please select a patient first.")
        )
        context = {"category_name": category_name, "forms": {}}
        return render(request, "emr/lab/father_form.html", context)

    patient = get_object_or_404(Patient, id=selected_patient_id)
    logger.info(f"Selected patient: {patient}")

    # Get the dynamic test models and form classes for the category.
    test_models = get_tests_for_category(category_name)
    lab_forms = get_lab_forms_for_category(category_name)
    logger.info(
        f"Test models for '{category_name}': {[model.__name__ for model in test_models]}"
    )

    # Prepare a dict to hold the forms, and a parallel dict for prefixes.
    form_instances = {}
    prefix_map = {}

    # For a fresh form, always instantiate a new (unsaved) record with a unique prefix.
    for i, test_model in enumerate(test_models):
        form_class = lab_forms.get(test_model.__name__)
        if form_class:
            prefix = f"test_{i}"  # e.g. "test_0", "test_1", etc.
            prefix_map[test_model.__name__] = prefix
            # Create a new blank form with the given prefix.
            form_instance = form_class(prefix=prefix, request=request, instance=None)
            form_instances[test_model.__name__] = form_instance
            logger.info(
                f"Created new form for model {test_model.__name__} with prefix '{prefix}'."
            )
        else:
            logger.warning(f"No form class found for {test_model.__name__}")

    # Get the category name based on the current language.
    language_code = get_language()
    category = get_object_or_404(Category, name=category_name)

    # Select the appropriate name column based on the language.
    category_name_field = (
        f"{language_code}_name"
        if hasattr(category, f"{language_code}_name")
        else "en_name"
    )
    category_name = getattr(category, category_name_field)

    if request.method == "POST":
        logger.info("Processing POST data for lab category view.")
        all_valid = True
        new_form_instances = {}

        # Iterate over each existing form, re-bind with POST data, using the same prefix.
        for test_name, old_form in form_instances.items():
            prefix = prefix_map[test_name]
            form_class = old_form.__class__
            bound_form = form_class(
                prefix=prefix, request=request, data=request.POST, files=request.FILES
            )

            if bound_form.is_valid():
                if bound_form.has_changed():
                    # Call save(commit=True) to run the full save logic, including event registration.
                    lab_record = bound_form.save(commit=True)
                    bound_form.save_m2m()  # Save many-to-many relationships
                    logger.info(f"Saved lab record for {test_name} (prefix: {prefix}).")
                else:
                    logger.info(
                        f"No data provided for {test_name} (prefix: {prefix}); skipping save."
                    )

                # Reinitialize the form to be blank after processing
                new_form_instances[test_name] = form_class(
                    prefix=prefix, request=request, instance=None
                )
            else:
                all_valid = False
                logger.warning(
                    f"Form errors in {test_name} (prefix: {prefix}): {bound_form.errors}"
                )
                new_form_instances[test_name] = bound_form

        form_instances = new_form_instances

        if all_valid:
            messages.success(request, _("All lab test data successfully saved."))
        else:
            messages.error(request, _("There were errors in your submission."))

    logger.info(f"Rendering template with forms: {list(form_instances.keys())}")
    context = {
        "segment": category_name,
        "parent": "investigations",
        "page_title": category_name,
        "category_name": category_name,
        "forms": form_instances,
    }
    return render(request, "emr/lab/father_form.html", context)


def investigations(request):
    return render(request, "emr/lab/father_form.html", {})
