from django.db import models
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from apps.emr.identity.models import Patient
from apps.emr.lab.models import TestMeta


class BaseSheet(models.Model):
    en_question = models.TextField(_("English Question"))
    fa_question = models.TextField(_("Persian Question"))
    coefficient = models.SmallIntegerField(_("Coefficient"))

    class Meta:
        abstract = True


class AbstractCategory(models.Model):
    en_name = models.CharField(_("English Name"), max_length=256)  # ASCII text
    fa_name = models.CharField(_("Persian Name"), max_length=256)  # Unicode text
    description = models.TextField(_("Description"))  # Large text field

    class Meta:
        abstract = True

    def __str__(self):
        return self.en_name


class Meta(models.Model):
    lab_testmeta = models.ForeignKey(
        TestMeta,  # Direct reference to the imported TestMeta model
        on_delete=models.CASCADE,
        unique=True,
        verbose_name=_("Lab Test Meta ID"),
    )
    lowest = models.DecimalField(_("Lowest Value"), max_digits=10, decimal_places=2)
    vector = models.PositiveSmallIntegerField(_("Vector"))
    highest = models.DecimalField(_("Highest Value"), max_digits=10, decimal_places=2)
    instruction_en = models.TextField(_("Instructions in English"))
    instruction_fa = models.TextField(_("Instructions in Persian"))
    reference_article = models.CharField(_("Reference Article"), max_length=256)
    validator_fa = models.CharField(_("Persian Validator"), max_length=256)

    level_1_en = models.CharField(_("Level 1 in English"), max_length=256)
    level_1_fa = models.CharField(_("Level 1 in Persian"), max_length=256)
    level_2_en = models.CharField(_("Level 2 in English"), max_length=256)
    level_2_fa = models.CharField(_("Level 2 in Persian"), max_length=256)
    level_3_en = models.CharField(_("Level 3 in English"), max_length=256)
    level_3_fa = models.CharField(_("Level 3 in Persian"), max_length=256)
    level_4_en = models.CharField(_("Level 4 in English"), max_length=256)
    level_4_fa = models.CharField(_("Level 4 in Persian"), max_length=256)
    level_5_en = models.CharField(_("Level 5 in English"), max_length=256)
    level_5_fa = models.CharField(_("Level 5 in Persian"), max_length=256)
    level_6_en = models.CharField(_("Level 6 in English"), max_length=256)
    level_6_fa = models.CharField(_("Level 6 in Persian"), max_length=256)
    level_7_en = models.CharField(_("Level 7 in English"), max_length=256)
    level_7_fa = models.CharField(_("Level 7 in Persian"), max_length=256)
    level_8_en = models.CharField(_("Level 8 in English"), max_length=256)
    level_8_fa = models.CharField(_("Level 8 in Persian"), max_length=256)
    level_9_en = models.CharField(_("Level 9 in English"), max_length=256)
    level_9_fa = models.CharField(_("Level 9 in Persian"), max_length=256)
    level_10_en = models.CharField(_("Level 10 in English"), max_length=256)
    level_10_fa = models.CharField(_("Level 10 in Persian"), max_length=256)

    class Meta:
        verbose_name = _("Meta")
        verbose_name_plural = _("Meta")


class PatientRecord(models.Model):
    patient = models.ForeignKey(
        Patient,  # Direct reference to the imported Patient model
        on_delete=models.CASCADE,
        verbose_name=_("Patient ID"),
    )
    date = models.DateField(_("Date"), null=True, blank=True)
    time = models.TimeField(_("Time"), null=True, blank=True)

    # Dynamically create fields for q_1 to q_i
    @classmethod
    def define_questions(cls, i):
        fields = {}
        for q in range(1, i + 1):
            field_name = f"q_{q}"
            fields[field_name] = models.PositiveSmallIntegerField(
                _(f"Question {q}"), null=True, blank=True
            )
        return fields

    class Meta:
        abstract = True


class YEMSQCategories(AbstractCategory):
    pass


class YEMSQSheet(BaseSheet):
    Category = models.ForeignKey(
        YEMSQCategories,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Subscore"),
    )

    class Meta:
        verbose_name = _("YEMSQ Sheet")
        verbose_name_plural = _("YEMSQ Questions")


class YEMSQ(PatientRecord):
    # Dynamically define fields for q_1 to q_75
    for q in range(1, 76):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("YEMSQ Record")
        verbose_name_plural = _("YEMSQ Records")


class McSCISSheet(BaseSheet):

    class Meta:
        verbose_name = _("McSCI-S Sheet")
        verbose_name_plural = _("McSCI-S Questions")


class McSCIS(PatientRecord):
    for q in range(1, 47):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("McSCI-S Record")
        verbose_name_plural = _("McSCI-S Records")


############################
#                          #
#  PHQ                     #
#                          #
############################


class PHQ010Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Somatoform disorders)")
        verbose_name_plural = _("PHQ Questions (Somatoform disorders)")


class PHQ010(PatientRecord):
    for q in range(1, 13):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Somatoform disorders)")
        verbose_name_plural = _("PHQ Records (Somatoform disorders)")


class PHQ011Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Somatoform disorders - Severity)")
        verbose_name_plural = _("PHQ Questions (Somatoform disorders - Severity)")


class PHQ011(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Somatoform disorders - Severity)")
        verbose_name_plural = _("PHQ Records (Somatoform disorders - Severity)")


class PHQ020Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Depressive disorders)")
        verbose_name_plural = _("PHQ Questions (Depressive disorders)")


class PHQ020(PatientRecord):
    for q in range(1, 9):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Depressive disorders)")
        verbose_name_plural = _("PHQ Records (Depressive disorders)")


class PHQ021Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Depressive disorders - Severity)")
        verbose_name_plural = _("PHQ Questions (Depressive disorders - Severity)")


class PHQ021(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Depressive disorders - Severity)")
        verbose_name_plural = _("PHQ Records (Depressive disorders - Severity)")


class PHQ030Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Panic disorder - part 1)")
        verbose_name_plural = _("PHQ Questions (Panic disorder - part 1)")


class PHQ030(PatientRecord):
    for q in range(1, 4):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Panic disorder - part 1)")
        verbose_name_plural = _("PHQ Records (Panic disorder - part 1)")


class PHQ040Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Panic disorder - part 2)")
        verbose_name_plural = _("PHQ Questions (Panic disorder - part 2)")


class PHQ040(PatientRecord):
    for q in range(1, 11):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Panic disorder - part 2)")
        verbose_name_plural = _("PHQ Records (Panic disorder - part 2)")


class PHQ041Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Panic disorder - Severity)")
        verbose_name_plural = _("PHQ Questions (Panic disorder - Severity)")


class PHQ041(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Panic disorder - Severity)")
        verbose_name_plural = _("PHQ Records (Panic disorder - Severity)")


class PHQ050Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Anxiety disorders)")
        verbose_name_plural = _("PHQ Questions (Anxiety disorders)")


class PHQ050(PatientRecord):
    for q in range(1, 7):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Anxiety disorders)")
        verbose_name_plural = _("PHQ Records (Anxiety disorders)")


class PHQ051Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Anxiety disorders - Severity)")
        verbose_name_plural = _("PHQ Questions (Anxiety disorders - Severity)")


class PHQ051(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Anxiety disorders - Severity)")
        verbose_name_plural = _("PHQ Records (Anxiety disorders - Severity)")


class PHQ060Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Eating disorders - part 1)")
        verbose_name_plural = _("PHQ Questions (Eating disorders - part 1)")


class PHQ060(PatientRecord):
    for q in range(1, 3):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Eating disorders - part 1)")
        verbose_name_plural = _("PHQ Records (Eating disorders - part 1)")


class PHQ070Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Eating disorders - part 2)")
        verbose_name_plural = _("PHQ Questions (Eating disorders - part 2)")


class PHQ070(PatientRecord):
    for q in range(1, 4):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Eating disorders - part 2)")
        verbose_name_plural = _("PHQ Records (Eating disorders - part 2)")


class PHQ080Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Eating disorders - part 3)")
        verbose_name_plural = _("PHQ Questions (Eating disorders - part 3)")


class PHQ080(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Eating disorders - part 3)")
        verbose_name_plural = _("PHQ Records (Eating disorders - part 3)")


class PHQ081Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Eating disorders - Severity)")
        verbose_name_plural = _("PHQ Questions (Eating disorders - Severity)")


class PHQ081(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Eating disorders - Severity)")
        verbose_name_plural = _("PHQ Records (Eating disorders - Severity)")


class PHQ090Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Alcohol consumption)")
        verbose_name_plural = _("PHQ Questions (Alcohol consumption)")


class PHQ090(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Alcohol consumption)")
        verbose_name_plural = _("PHQ Records (Alcohol consumption)")


class PHQ100Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Alcohol abuse disorder)")
        verbose_name_plural = _("PHQ Questions (Alcohol abuse disorder)")


class PHQ100(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Alcohol abuse disorder)")
        verbose_name_plural = _("PHQ Records (Alcohol abuse disorder)")


class PHQ101Sheet(BaseSheet):

    class Meta:
        verbose_name = _("PHQ Sheet (Alcohol abuse disorder - Severity)")
        verbose_name_plural = _("PHQ Questions (Alcohol abuse disorder - Severity)")


class PHQ101(PatientRecord):
    for q in range(1, 1):
        locals()[f"q_{q}"] = models.PositiveSmallIntegerField(
            _(f"Question {q}"), null=True, blank=True
        )

    class Meta:
        verbose_name = _("PHQ Record (Alcohol abuse disorder - Severity)")
        verbose_name_plural = _("PHQ Records (Alcohol abuse disorder - Severity)")
