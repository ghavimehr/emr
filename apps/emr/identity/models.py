from django.db import models
from django_jalali.db import models as jmodels
from django.core.validators import RegexValidator, MaxValueValidator
from django.db.models import JSONField
from django.contrib.auth import get_user_model
from datetime import date
import jdatetime


from apps.common.models_localization import LocalizedNameMixin
# from apps.common.utils_localization import get_localized_name

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

    # birthday = jmodels.jDateField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    @property
    def jbirthday(self):
        """
        Returns the birthday in Jalali (Persian) calendar as a jdatetime.date,
        or None if no birthday is set.
        """
        if not self.birthday:
            return None
        return jdatetime.date.fromgregorian(date=self.birthday)

    @property
    def age(self):
        """
        Returns the patient's age in whole years, rounding by months:
        if they've passed ≥6 months since their last birthday, round up by 1.
        """
        if not self.birthday:
            return None

        today = date.today()
        years = today.year - self.birthday.year
        month_diff = today.month - self.birthday.month
        if today.day < self.birthday.day:
            month_diff -= 1

        if month_diff < 0:
            years -= 1
            month_diff += 12

        # round up if 6 or more months past last birthday
        if month_diff >= 6:
            years += 1

        return years


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

    ethnicity = models.JSONField(default=dict, blank=True)
    @property
    def ethnicity_display(self) -> str:
        ethnicity_data = self.ethnicity or {}
        selected_ids = [int(iid) for iid, val in ethnicity_data.items() if val == 1]
        qs = Ethnicity.objects.filter(id__in=selected_ids)
        # Join the localized names with commas
        names = [str(ins) for ins in qs]
        return ", ".join(names) if names else "---"
    
    insurance = models.JSONField(default=dict, blank=True)
    @property
    def insurances_display(self) -> str:
        insurance_data = self.insurance or {}
        selected_ids = [int(iid) for iid, val in insurance_data.items() if val == 1]
        qs = Insurance.objects.filter(id__in=selected_ids)
        # Join the localized names with commas
        names = [str(ins) for ins in qs]
        return ", ".join(names) if names else "---"
    
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

    def __str__(self):
        return f"PID: {self.patient_id} - {self.first_name} {self.last_name}"

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["ssn"]),
            models.Index(fields=["patient_id"]),
        ]




class MaritalStatus(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    name_fa = models.CharField(max_length=30, blank=True)



class EducationLevel(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_fa = models.CharField(max_length=20, blank=True)




class BloodGroup(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Gender(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50, blank=True)



class LanguageOption(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    name_fa = models.CharField(max_length=10, blank=True)




class Insurance(LocalizedNameMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    name_fa = models.CharField(max_length=20, blank=True)




class Ethnicity(LocalizedNameMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    name_fa = models.CharField(max_length=20, blank=True)



class DominantHand(LocalizedNameMixin, models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    name_fa = models.CharField(max_length=30, blank=True)


class Occupation(LocalizedNameMixin, models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    name_fa = models.CharField(max_length=100, blank=True, null=True)


class Secretarytags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
