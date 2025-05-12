from django.db import models
from django_jalali.db import models as jmodels
from django.core.validators import RegexValidator, MaxValueValidator
from django.db.models import JSONField
from django.contrib.auth import get_user_model


User = get_user_model()


class Patient(models.Model):
    """
    Stores the basic identification/demographic info for each patient.
    """

    id = models.BigAutoField(primary_key=True)

    patient_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    patient_id_alternative = models.PositiveIntegerField(
        unique=True, null=True, blank=True
    )

    first_name = models.CharField(max_length=100, null=True, blank=True)

    last_name = models.CharField(max_length=100, null=True, blank=True)

    ssn = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",  # Must be exactly 10 digits if provided
                message="Patient ID must be exactly 10 digits.",
            )
        ],
    )

    birthday = jmodels.jDateField(null=True, blank=True)

    ethnicity = models.JSONField(default=dict, blank=True)

    insurance = models.JSONField(default=dict, blank=True)

    dominanthand = models.ForeignKey(
        "DominantHand", null=True, blank=True, on_delete=models.SET_NULL
    )

    payment_label = models.CharField(
        max_length=50,
        choices=[("NC", "No Cost"), ("VIP", "VIP"), ("STD", "Standard")],
        default="STD",
    )

    tags = models.TextField(blank=True)

    notes = models.TextField(null=True, blank=True)

    address = models.TextField(null=True, blank=True)

    occupation = models.ForeignKey(
        "Occupation", null=True, blank=True, on_delete=models.SET_NULL
    )

    edit_history = models.JSONField(default=dict, blank=True)
    report = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"PID: {self.patient_id} - {self.first_name} {self.last_name}"

    def get_selected_ethnicities(self):
        """
        Returns a list of Ethnicity objects the user selected.
        """
        # Ensure ethnicity is a dictionary, if not, use an empty dictionary
        ethnicities_data = self.ethnicity if isinstance(self.ethnicity, dict) else {}

        selected_ids = [int(eid) for eid, val in ethnicities_data.items() if val == 1]

        # Fetch from DB based on selected ids
        return Ethnicity.objects.filter(id__in=selected_ids)

    def get_selected_insurances(self):
        """
        Returns a list of Insurance objects the user selected.
        """
        # Ensure insurance is a dictionary, if not, use an empty dictionary
        insurance_data = self.insurance if isinstance(self.insurance, dict) else {}

        selected_ids = [int(iid) for iid, val in insurance_data.items() if val == 1]

        # Fetch from DB based on selected ids
        return Insurance.objects.filter(id__in=selected_ids)

    marital_status = models.ForeignKey(
        "MaritalStatus", null=True, blank=True, on_delete=models.SET_NULL
    )

    education_level = models.ForeignKey(
        "EducationLevel", null=True, blank=True, on_delete=models.SET_NULL
    )

    blood_group = models.ForeignKey(
        "BloodGroup", null=True, blank=True, on_delete=models.SET_NULL
    )

    gender = models.ForeignKey(
        "Gender", null=True, blank=True, on_delete=models.SET_NULL
    )

    language_option = models.ForeignKey(
        "LanguageOption", null=True, blank=True, on_delete=models.SET_NULL
    )

    phone_regex = RegexValidator(
        regex=r"^0\d{10}$", message="Must start with 0 and be 11 digits total."
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=11, blank=True, null=True
    )

    messenger1 = models.CharField(
        validators=[phone_regex], max_length=11, blank=True, null=True
    )

    messenger2 = models.CharField(
        validators=[phone_regex], max_length=11, blank=True, null=True
    )

    height = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(999)]
    )

    weight = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(999)]
    )

    insurances = models.ManyToManyField("Insurance", blank=True)

    Secretarytags = models.ManyToManyField("Secretarytags", blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["ssn"]),
            models.Index(fields=["patient_id"]),
        ]




class MaritalStatus(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    name_fa = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_fa = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class BloodGroup(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Gender(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class LanguageOption(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    name_fa = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name


class Insurance(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    name_fa = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Ethnicity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    name_fa = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class DominantHand(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    name_fa = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name


class Occupation(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    name_fa = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.name_fa if self.name_fa else "Unknown"


class Secretarytags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
