from django import forms
from django.utils.translation import get_language
from django.utils import timezone
import datetime
import jdatetime

from .models import *


class IdentityForm(forms.ModelForm):
    """
    Form for creating or updating a Patient (Identity) with language-dependent options.
    """

    # Custom fields (not directly in the Patient model)
    occupation_search = forms.CharField(max_length=100, required=False)
    ethnicities_field = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple, required=False
    )
    Secretary_tags_field = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple
    )
    insurances_field = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple, required=False
    )

    class Meta:
        model = Patient
        fields = [
            "patient_id",
            "first_name",
            "last_name",
            "ssn",
            "birthday",
            "marital_status",
            "education_level",
            "blood_group",
            "gender",
            "language_option",
            "phone",
            "messenger1",
            "messenger2",
            "height",
            "weight",
            "dominanthand",
            "payment_label",
            "tags",
            "address",
            "occupation",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        lang = get_language()  # Detect the user's current language

        # Let Django accept multiple date input formats: "1401-01-01" or "1401/01/01"
        self.fields["birthday"].input_formats = ["%Y-%m-%d", "%Y/%m/%d"]

        # Load Secretary Tags
        all_tags = Secretarytags.objects.all()
        self.fields["Secretary_tags_field"].choices = [
            (str(t.id), t.name) for t in all_tags
        ]

        # Load Ethnicities (Language-Specific)
        all_ethnicities = Ethnicity.objects.all().order_by("name")
        self.fields["ethnicities_field"].choices = [
            (str(e.id), e.name_fa if lang == "fa" else e.name) for e in all_ethnicities
        ]

        # Load Insurances (Language-Specific)
        all_insurances = Insurance.objects.all().order_by("name")
        self.fields["insurances_field"].choices = [
            (str(e.id), e.name_fa if lang == "fa" else e.name) for e in all_insurances
        ]

        # Handle pre-filled data when editing an existing Patient
        if self.instance.pk:
            # Ethnicities
            selected_eth_ids = [
                eid for eid, val in self.instance.ethnicity.items() if val == 1
            ]
            self.fields["ethnicities_field"].initial = selected_eth_ids

            # Insurances
            selected_ins_ids = [
                iid for iid, val in self.instance.insurance.items() if val == 1
            ]
            self.fields["insurances_field"].initial = selected_ins_ids

            # Secretary Tags
            selected_tags = list(
                self.instance.Secretarytags.values_list("id", flat=True)
            )
            self.fields["Secretary_tags_field"].initial = selected_tags

        # Default birthday (if not set)
        if not self.instance.pk or not self.instance.birthday:
            self.fields["birthday"].initial = "1340/01/01"

        # Make occupation read-only
        self.fields["occupation"].widget.attrs["readonly"] = True

        # Customize widgets (placeholders, CSS classes, etc.)
        self.fields["height"].widget = forms.NumberInput(
            attrs={
                "class": "rounded-lg block w-full p-2.5 bg-white dark:bg-gray-700 border "
                "border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white",
                "style": "direction: ltr; text-align: left;",
                "placeholder": "e.g. 180 (cm)",
            }
        )
        self.fields["weight"].widget = forms.NumberInput(
            attrs={
                "class": "rounded-lg block w-full p-2.5 bg-white dark:bg-gray-700 border "
                "border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white",
                "style": "direction: ltr; text-align: left;",
                "placeholder": "e.g. 75 (kg)",
            }
        )

        self.fields["phone"].widget.attrs.update(
            {"style": "direction: ltr; text-align: left;", "placeholder": "09*********"}
        )
        self.fields["messenger1"].widget.attrs.update(
            {"style": "direction: ltr; text-align: left;", "placeholder": "09*********"}
        )
        self.fields["messenger2"].widget.attrs.update(
            {"style": "direction: ltr; text-align: left;", "placeholder": "09*********"}
        )

    def save(self, commit=True):
        """
        Custom save method to handle JSON fields for ethnicity, insurance, and history tracking.
        """
        patient = super().save(commit=False)

        # Convert selected ethnicities to JSON {id: 0 or 1}
        chosen_eth = self.cleaned_data.get("ethnicities_field", [])
        new_ethnicities = {
            str(e.id): 1 if str(e.id) in chosen_eth else 0
            for e in Ethnicity.objects.all()
        }
        patient.ethnicity = new_ethnicities

        # Convert selected insurances to JSON {id: 0 or 1}
        chosen_ins = self.cleaned_data.get("insurances_field", [])
        new_ins = {
            str(i.id): 1 if str(i.id) in chosen_ins else 0
            for i in Insurance.objects.all()
        }
        patient.insurance = new_ins

        # Handle user-typed occupation (Language-Specific)
        new_occ = self.cleaned_data.get("occupation_search", "").strip()
        if new_occ:
            lang = get_language()
            if lang == "fa":
                occ_obj, _ = Occupation.objects.get_or_create(
                    name_fa=new_occ
                )  # Store in Persian
            else:
                occ_obj, _ = Occupation.objects.get_or_create(
                    name=new_occ
                )  # Store in English
            patient.occupation = occ_obj

        # If this is an edit, update edit history
        if patient.pk:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_str = (
                self.request.user.username
                if self.request and self.request.user.is_authenticated
                else "unknown"
            )
            history = patient.edit_history or {}
            history[now_str] = user_str
            patient.edit_history = history

        if commit:
            patient.save()
            patient.Secretarytags.set(self.cleaned_data["Secretary_tags_field"])

        return patient
