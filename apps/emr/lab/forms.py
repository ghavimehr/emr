from django import forms
from django.utils.translation import gettext as _
from django.utils import timezone
from django.forms import BooleanField
import jdatetime

from .widgets import TagWidget
from .models import *
from apps.emr.events.models import *
from .utils import get_tests_for_category

import logging

logger = logging.getLogger(__name__)


class DynamicLabTestForm(forms.ModelForm):
    """
    A dynamic form to generate lab test forms while excluding certain fields automatically.
    It automatically sets the current user, input_date, patient, and creates event records.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # 1. Exclude fields that must be set programmatically.
        exclude_fields = {"id", "patient", "input_date", "registered_event", "user"}
        for field_name in exclude_fields:
            if field_name in self.fields:
                del self.fields[field_name]

        # 2. Assign TagWidget if the 'tag' field is present.
        if "tag" in self.fields:
            self.fields["tag"].widget = TagWidget(
                attrs={
                    "data-placeholder": _("Select or create tags"),
                    "class": "select2-tags",
                    "style": "width: 100%;",
                }
            )

        # 3. Style the other fields (skip 'date', 'tag', 'performer').
        special_fields = {"date", "tag", "performer"}
        for field_name, field in self.fields.items():
            if field_name in special_fields:
                continue
            if isinstance(field, BooleanField):
                field.widget = forms.CheckboxInput(attrs={"class": "w-5 h-5"})
            elif getattr(field.widget, "input_type", None) == "checkbox":
                existing_class = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (existing_class + " w-5 h-5").strip()
            else:
                existing_class = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (
                    existing_class
                    + " rounded-lg block w-full p-2.5 bg-white dark:bg-gray-700 "
                    "border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white"
                ).strip()

        # 4. Reorder fields so date -> normal fields -> performer -> tag.
        desired_order = []
        if "date" in self.fields:
            self.fields["date"].input_formats = ["%Y/%m/%d", "%Y-%m-%d"]
            self.fields["date"].widget = forms.TextInput(
                attrs={"class": "test-date", "placeholder": _("Select test date")}
            )

        normal_fields = [
            f for f in self.fields if f not in {"date", "performer", "tag"}
        ]
        desired_order.extend(normal_fields)
        if "performer" in self.fields:
            desired_order.append("performer")
        if "tag" in self.fields:
            desired_order.append("tag")
        self.order_fields(desired_order)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 5. Set current user, date, and patient from session.
        if self.request and self.request.user.is_authenticated:
            instance.user = self.request.user
        instance.input_date = timezone.now().date()
        selected_patient_id = self.request.session.get("selected_patient_id")
        if selected_patient_id:
            from apps.emr.identity.models import Patient

            patient = Patient.objects.get(id=selected_patient_id)
            instance.patient = patient

        # 6. Convert Jalali date to Gregorian if present.
        if "date" in self.cleaned_data:
            jalali_date_str = self.cleaned_data["date"]
            try:
                # Use the correct format to match the input; adjust if needed.
                jdt = jdatetime.datetime.strptime(jalali_date_str, "%Y/%m/%d")
                instance.date = jdt.togregorian().date()
            except ValueError:
                # You can log the error or handle it accordingly.
                pass

        # 7. Save the instance.
        if commit:
            instance.save()
            if "tag" in self.cleaned_data:
                instance.tag.set(self.cleaned_data["tag"])
                logger.info(
                    "Updated ManyToMany tag field for %s with tags: %s",
                    instance,
                    self.cleaned_data["tag"],
                )

            # 8. (Event registration logic
            events_created = []
            logger.info("Model name: %s", instance._meta.object_name)
            try:
                testmeta = TestMeta.objects.get(name__iexact=instance._meta.object_name)
                logger.info("Found TestMeta: %s", testmeta)
            except TestMeta.DoesNotExist:
                logger.warning("No TestMeta found for: %s", instance._meta.object_name)
                testmeta = None

            if testmeta:
                test_type = testmeta.testtype
                event_types = test_type.eventtypes.all()
                for event_type in event_types:
                    now = timezone.now()
                    new_event = Event.objects.create(
                        event_type=event_type,
                        date=now.date(),
                        time=now.time(),
                        patient_id=selected_patient_id,
                        user=(
                            self.request.user
                            if self.request and self.request.user.is_authenticated
                            else None
                        ),
                    )
                    events_created.append(new_event)
            preferred_event = None
            for event in events_created:
                if event.event_type.id == 43:
                    preferred_event = event
                    break
            if not preferred_event and events_created:
                preferred_event = events_created[0]
            if preferred_event:
                instance.registered_event = preferred_event
                instance.save(update_fields=["registered_event"])

            logger.info("Cleaned tag data: %s", self.cleaned_data.get("tag"))
        return instance

    class Meta:
        model = None  # Assigned dynamically in the view.
        exclude = ("patient", "user", "input_date", "registered_event")


def make_custom_lab_form(model_cls):
    """Dynamically creates a form class for the given lab test model."""

    class Meta(DynamicLabTestForm.Meta):
        model = model_cls

    CustomLabForm = type(
        f"{model_cls.__name__}Form", (DynamicLabTestForm,), {"Meta": Meta}
    )
    return CustomLabForm


def get_lab_forms_for_category(category_name):
    """
    Returns a dictionary mapping each lab test model's name to its custom form class.
    """
    test_models = get_tests_for_category(category_name)
    forms_dict = {}
    for test_model in test_models:
        forms_dict[test_model.__name__] = make_custom_lab_form(test_model)
    return forms_dict
