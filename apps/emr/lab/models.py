# apps/emr/lab/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from apps.emr.identity.models import *
import datetime
import pytz

User = get_user_model()


def get_tehran_today():
    tehran_tz = pytz.timezone("Asia/Tehran")
    return datetime.datetime.now(tehran_tz).date()


class Category(models.Model):
    """
    Is mostly based on the test's platforms
    the main usage of this class is to organize test's into difirent webpages.
    """

    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("Test Category Name")
    )
    en_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("English Test Category Name"),
    )
    fa_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Persian Test Category Name"),
    )

    def __str__(self):
        return self.name


class Testtype(models.Model):
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("Test Type Name")
    )
    fa_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Persian Test Type Name"),
    )
    # Add many-to-many field connecting Testtype to the events app’s EventType model.
    eventtypes = models.ManyToManyField(
        "events.EventType",
        blank=True,
        related_name="testtypes",
        verbose_name=_("Event Types"),
    )

    def __str__(self):
        return self.name


class TestMeta(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Test Name"))
    fa_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Persian Test Name"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name=_("Category"),
    )
    testtype = models.ForeignKey(
        Testtype,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name=_("Testtype"),
        default=1,
    )
    all_required = models.BooleanField(default=False, verbose_name=_("All Required"))
    access = models.JSONField(default=dict, verbose_name=_("Access Permissions"))

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Tag Name"))
    fa_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Persian Tag Name"),
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class AbstractPerformer(models.Model):
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("Performer Name")
    )
    fa_name = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Persian Performer Name"),
    )

    class Meta:
        abstract = True


# Concrete performer model for Blood Tests category:
class BloodTestPerformer(AbstractPerformer):
    class Meta:
        verbose_name = _("Blood Test Performer")
        verbose_name_plural = _("Blood Test Performers")

    def __str__(self):
        return self.name


class LpPerformer(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
    fanme = models.CharField(max_length=255, verbose_name=_("Persian Nanme"))
    family = models.CharField(max_length=255, verbose_name=_("Family"))
    ffamily = models.CharField(max_length=255, verbose_name=_("Persian Family"))
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("User")
    )
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Address")
    )

    class Meta:
        verbose_name = _("CSF Test Performer")
        verbose_name_plural = _("CSF Test Performers")

    def __str__(self):
        return self.name


class Psychometrician(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
    fanme = models.CharField(max_length=255, verbose_name=_("Persian Nanme"))
    family = models.CharField(max_length=255, verbose_name=_("Family"))
    ffamily = models.CharField(max_length=255, verbose_name=_("Persian Family"))
    education = models.ForeignKey(
        EducationLevel, on_delete=models.CASCADE, verbose_name=_("Education Level")
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("User")
    )
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Address")
    )

    class Meta:
        verbose_name = _("Psychometrician")
        verbose_name_plural = _("Psychometricians")

    def __str__(self):
        return self.name


class BaseTest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(default=get_tehran_today, verbose_name=_("Test Date"))
    tag = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags"))
    registered_event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Registered Event"),
    )

    # Note: Remove the generic performer field. Instead, add a performer field in each concrete test
    # that points to the appropriate performer model.
    class Meta:
        abstract = True


DECIMAL_3_1 = {
    "max_digits": 3,
    "decimal_places": 1,
    "validators": [MinValueValidator(0)],
    "null": True,
    "blank": True,
}


DECIMAL_4_1 = {
    "max_digits": 4,
    "decimal_places": 1,
    "validators": [MinValueValidator(0)],
    "null": True,
    "blank": True,
}

DECIMAL_5_3 = {
    "max_digits": 5,
    "decimal_places": 3,
    "validators": [MinValueValidator(0)],
    "null": True,
    "blank": True,
}

DECIMAL_6_3 = {
    "max_digits": 6,
    "decimal_places": 3,
    "validators": [MinValueValidator(0)],
    "null": True,
    "blank": True,
}


# Example: CBC test is assumed to belong to the "Blood Tests" category.
class CBC(BaseTest):
    # Now reference the category-specific performer table.
    performer = models.ForeignKey(
        BloodTestPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Laboratory Name"),
    )
    WBC = models.DecimalField(**DECIMAL_3_1, verbose_name=_("WBC"))
    RBC = models.DecimalField(**DECIMAL_3_1, verbose_name=_("RBC"))
    hemoglobin = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Hemoglobin"))
    hemotocrite = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Hematocrit"))
    MCV = models.DecimalField(**DECIMAL_3_1, verbose_name=_("MCV"))
    MCHC = models.DecimalField(**DECIMAL_3_1, verbose_name=_("MCHC"))
    RDW_CV = models.DecimalField(**DECIMAL_3_1, verbose_name=_("RDW-CV"))
    RDW_SD = models.DecimalField(**DECIMAL_3_1, verbose_name=_("RDW-SD"))
    platelets = models.PositiveSmallIntegerField(
        verbose_name=_("Platelets"), null=True, blank=True
    )
    MPV = models.DecimalField(**DECIMAL_3_1, verbose_name=_("MPV"))
    PDW = models.DecimalField(**DECIMAL_3_1, verbose_name=_("PDW"))
    PCT = models.DecimalField(**DECIMAL_6_3, verbose_name=_("PCT"))
    neutrophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Neutrophils"))
    lymphocytes = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Lymphocytes"))
    monocytes = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Monocytes"))
    eosinophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Eosinophils"))
    basophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Basophils"))

    def clean(self):
        """
        Enforce an "all-or-none" rule: if the user provides any CBC data,
        then all fields must be filled. Also check that the sum of the
        differentiation values does not exceed 100.
        """
        super().clean()
        # List of all fields that must be provided if any is filled.
        field_names = [
            "WBC",
            "RBC",
            "hemoglobin",
            "hemotocrite",
            "MCV",
            "MCHC",
            "RDW_CV",
            "RDW_SD",
            "platelets",
            "MPV",
            "PDW",
            "PCT",
            "neutrophils",
            "lymphocytes",
            "monocytes",
            "eosinophils",
            "basophils",
        ]
        # Gather each field's value.
        field_values = {name: getattr(self, name) for name in field_names}
        any_filled = any(value is not None for value in field_values.values())
        all_filled = all(value is not None for value in field_values.values())

        # If the user starts filling in data but leaves some fields empty:
        if any_filled and not all_filled:
            missing = [name for name, value in field_values.items() if value is None]
            raise ValidationError(
                {
                    "__all__": _(
                        "If you provide any CBC data, all fields must be completed. Missing: %(fields)s"
                    )
                    % {"fields": ", ".join(missing)}
                }
            )

        # If all fields are blank, allow the test to be omitted.
        if not any_filled:
            return

        # Now that all fields are filled, check that the sum of the differentiation fields is valid.
        differentiation_sum = (
            self.neutrophils
            + self.lymphocytes
            + self.monocytes
            + self.eosinophils
            + self.basophils
        )

        if abs(differentiation_sum - 100) > 1:
            raise ValidationError(
                {"neutrophils": _("The sum of differentiation values must be 100.")}
            )

    class Meta:
        verbose_name = _("Complete Blood Count")

    def __str__(self):
        return _("CBC for patient: ") + str(self.patient)


class MetabolicProfile(BaseTest):
    # Now reference the category-specific performer table.
    performer = models.ForeignKey(
        BloodTestPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Laboratory Name"),
    )
    FBS = models.PositiveSmallIntegerField(
        verbose_name=_("FBS (Fast Plasma Glucose)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    BS = models.PositiveSmallIntegerField(
        verbose_name=_("BS (Random Plasma Glucose)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    twohPP = models.PositiveSmallIntegerField(
        verbose_name=_("2hPP (2-hours Post Prandial Plasma Glucose)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    OGGT = models.PositiveSmallIntegerField(
        verbose_name=_("OGTT (Oral Glucose Tolerance Test)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )

    HbA1c = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Hb A1c"))

    TC = models.PositiveSmallIntegerField(
        verbose_name=_("TC (Total Cholesterol)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    HDL = models.PositiveSmallIntegerField(
        verbose_name=_("HDL (High-Density Lipoprotein)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    LDL = models.PositiveSmallIntegerField(
        verbose_name=_("LDL (Low-Density Lipoprotein)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    VLDL = models.PositiveSmallIntegerField(
        verbose_name=_("VLDL (Low-Density Lipoprotein)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    TG = models.PositiveSmallIntegerField(
        verbose_name=_("TG (Triglycerides)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Metabolic Profile")

    def __str__(self):
        return _("Metabolic Profile for patient: ") + str(self.patient)


class TFT(BaseTest):
    # Now reference the category-specific performer table.
    performer = models.ForeignKey(
        BloodTestPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Laboratory Name"),
    )
    TSH = models.DecimalField(**DECIMAL_6_3, verbose_name=_("TSH"))
    T3 = models.DecimalField(**DECIMAL_6_3, verbose_name=_("T3"))
    freeT3 = models.DecimalField(**DECIMAL_6_3, verbose_name=_("freeT3"))
    T4 = models.DecimalField(**DECIMAL_5_3, verbose_name=_("T4 (mcrg/dl)"))
    T4_mol = models.DecimalField(**DECIMAL_4_1, verbose_name=_("T4 (nmol/l)"))
    freeT4 = models.DecimalField(**DECIMAL_6_3, verbose_name=_("freeT4"))
    AntiTPO = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Anti TPO Ab"))
    Tg = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Thyroglobulin"))
    AntiTg = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Anti Thyroglobulin Ab"))
    antiTSH = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Anti TSH Ab"))
    antiT3 = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Anti T3 Ab"))
    antiT4 = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Anti T4 Ab"))

    class Meta:
        verbose_name = _("Thyroid Function Test")

    def __str__(self):
        return _("Thyroid Function Test for patient: ") + str(self.patient)


class LFT(BaseTest):
    # Now reference the category-specific performer table.
    performer = models.ForeignKey(
        BloodTestPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Laboratory Name"),
    )
    SGPT = models.PositiveSmallIntegerField(
        verbose_name=_("SGPT (ALT)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )
    ALP = models.PositiveSmallIntegerField(
        verbose_name=_("Alkaline Phosphatase (ALP)"),
        validators=[MaxValueValidator(9990)],
        blank=True,
        null=True,
    )
    ALB = models.PositiveSmallIntegerField(
        verbose_name=_("Albumin"),
        validators=[MaxValueValidator(99)],
        blank=True,
        null=True,
    )
    BiliT = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Total Bilirubin"))
    BiliD = models.DecimalField(**DECIMAL_6_3, verbose_name=_("Total Bilirubin"))
    GGT = models.PositiveSmallIntegerField(
        verbose_name=_("GGT (Gamma-Glutamyl Transferase)"),
        validators=[MaxValueValidator(999)],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Liver Function Test")

    def __str__(self):
        return _("Liver Function Test for patient: ") + str(self.patient)


class CSF(BaseTest):
    # Note: For CSF, we consider only the lab values (excluding performer fields)
    performer_lab = models.ForeignKey(
        BloodTestPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Laboratory Name"),
    )
    performer_lp = models.ForeignKey(
        LpPerformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("LP Performer"),
    )
    WBC = models.DecimalField(**DECIMAL_4_1, verbose_name=_("WBC"))
    RBC = models.DecimalField(**DECIMAL_4_1, verbose_name=_("RBC"))
    neutrophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Neutrophils"))
    lymphocytes = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Lymphocytes"))
    monocytes = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Monocytes"))
    eosinophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Eosinophils"))
    basophils = models.DecimalField(**DECIMAL_3_1, verbose_name=_("Basophils"))
    glucose = models.DecimalField(**DECIMAL_4_1, verbose_name=_("Glucose"))
    protein = models.DecimalField(**DECIMAL_4_1, verbose_name=_("Protein"))
    ketone = models.DecimalField(**DECIMAL_4_1, verbose_name=_("Ketone"))
    AB42 = models.DecimalField(**DECIMAL_4_1, verbose_name=_("Amyloid Beta 1-42"))
    alpha_synuclein = models.DecimalField(
        **DECIMAL_4_1, verbose_name=_("Alpha Synuclein")
    )

    def clean(self):
        super().clean()
        field_names = [
            "WBC",
            "RBC",
            "neutrophils",
            "lymphocytes",
            "monocytes",
            "eosinophils",
            "basophils",
            "glucose",
            "protein",
            "ketone",
            "AB42",
            "alpha_synuclein",
        ]
        field_values = {
            name: (
                getattr(self, name) if getattr(self, name) not in ("", None) else None
            )
            for name in field_names
        }
        any_filled = any(value is not None for value in field_values.values())
        all_filled = all(value is not None for value in field_values.values())

        # If the user starts filling in data but leaves some fields empty:
        if any_filled and not all_filled:
            missing = [name for name, value in field_values.items() if value is None]
            raise ValidationError(
                {
                    "__all__": _(
                        "If you provide any CBC data, all fields must be completed. Missing: %(fields)s"
                    )
                    % {"fields": ", ".join(missing)}
                }
            )

        # If all fields are blank, allow the test to be omitted.
        if not any_filled:
            return

        # Now that all fields are filled, safely sum the differentiation fields.
        try:
            differentiation_sum = sum(
                float(field_values[field])
                for field in [
                    "neutrophils",
                    "lymphocytes",
                    "monocytes",
                    "eosinophils",
                    "basophils",
                ]
            )
        except (TypeError, ValueError):
            raise ValidationError(
                _("One or more differentiation fields have invalid numeric values.")
            )

        if differentiation_sum > 100:
            raise ValidationError(
                {
                    "neutrophils": _(
                        "The sum of differentiation values must not exceed 100."
                    )
                }
            )

    def __str__(self):
        return _("CSF for patient: ") + str(self.patient)


class MMSE(BaseTest):
    performer = models.ForeignKey(
        Psychometrician,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Psychometrician"),
    )
    total = models.PositiveSmallIntegerField(
        verbose_name=_("Total MMSE Score"),
    )
    affective = models.PositiveSmallIntegerField(
        verbose_name=_("Affective"),
    )
    cognitive = models.PositiveSmallIntegerField(
        verbose_name=_("Cognitive"),
    )
    somatic = models.PositiveSmallIntegerField(
        verbose_name=_("Somatic"),
    )

    def clean(self):
        super().clean()
        # Define the fields that must follow the all-or-none rule.
        field_names = ["total", "affective", "cognitive", "somatic"]
        field_values = {name: getattr(self, name) for name in field_names}
        any_filled = any(value is not None for value in field_values.values())
        all_filled = all(value is not None for value in field_values.values())

        if any_filled and not all_filled:
            missing = [name for name, value in field_values.items() if value is None]
            raise ValidationError(
                {
                    "__all__": _(
                        "If you provide any MMSE data, all fields must be completed. Missing: %(fields)s"
                    )
                    % {"fields": ", ".join(missing)}
                }
            )

        if not any_filled:
            # Test omitted; do nothing.
            return

        # Now that all fields are provided, enforce cross-field validation:
        subscores = (self.affective or 0) + (self.cognitive or 0) + (self.somatic or 0)
        if self.total is not None and subscores != self.total:
            raise ValidationError(
                {"total": _("The total score must equal the sum of all subscores.")}
            )

    def __str__(self):
        return _("MMSE for patient: ") + str(self.patient)


from django.db import models


class PHQ(BaseTest):
    somatoform = models.BooleanField(
        default=False, verbose_name=_("Somatoform Disorder")
    )
    major_depression = models.BooleanField(default=False)
    other_depressions = models.BooleanField(default=False)
    panic = models.BooleanField(default=False)
    non_panic_anxiety = models.BooleanField(default=False)
    bulimia = models.BooleanField(default=False)
    binge_eating_disorder = models.BooleanField(default=False)
    alcohol_abuse = models.BooleanField(default=False)

    def __str__(self):
        return _("PHQ for patient: ") + str(self.patient)


class Moca(BaseTest):
    performer = models.ForeignKey(
        Psychometrician,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Performer"),
    )
    total = models.PositiveSmallIntegerField(
        verbose_name=_("Total Score"),
    )
    memory = models.PositiveSmallIntegerField(
        verbose_name=_("Memory"),
    )
    visuospatial = models.PositiveSmallIntegerField(
        verbose_name=_("Visuospatial"),
    )
    naming = models.PositiveSmallIntegerField(
        verbose_name=_("Naming"),
    )
    attention = models.PositiveSmallIntegerField(
        verbose_name=_("Attention"),
    )
    language = models.PositiveSmallIntegerField(
        verbose_name=_("Language"),
    )
    abstraction = models.PositiveSmallIntegerField(
        verbose_name=_("Abstraction"),
    )
    recall = models.PositiveSmallIntegerField(
        verbose_name=_("Recall"),
    )
    orientation = models.PositiveSmallIntegerField(
        verbose_name=_("Orientation"),
    )

    def clean(self):
        super().clean()
        field_names = [
            "total",
            "memory",
            "visuospatial",
            "naming",
            "attention",
            "language",
            "abstraction",
            "recall",
            "orientation",
        ]
        field_values = {name: getattr(self, name) for name in field_names}
        any_filled = any(value is not None for value in field_values.values())
        all_filled = all(value is not None for value in field_values.values())

        if any_filled and not all_filled:
            missing = [name for name, value in field_values.items() if value is None]
            raise ValidationError(
                {
                    "__all__": _(
                        "If you provide any MOCA data, all fields must be completed. Missing: %(fields)s"
                    )
                    % {"fields": ", ".join(missing)}
                }
            )

        if not any_filled:
            return

        # Cross-field check: total must equal the sum of subscores.
        subscores = (
            (self.memory or 0)
            + (self.visuospatial or 0)
            + (self.naming or 0)
            + (self.attention or 0)
            + (self.language or 0)
            + (self.abstraction or 0)
            + (self.recall or 0)
            + (self.orientation or 0)
        )
        if self.total is not None and subscores != self.total:
            raise ValidationError(
                {"total": _("The total score must equal the sum of all subscores.")}
            )

    def __str__(self):
        return _("MOCA for patient: ") + str(self.patient)
