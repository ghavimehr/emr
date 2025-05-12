from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext as _

from apps.emr.identity.models import Patient


class PulseType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    name_fa = models.CharField(max_length=100, verbose_name=_("Name (FA)"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Pulse Type")
        verbose_name_plural = _("Pulse Types")


class RTMS(models.Model):
    identity_patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, verbose_name=_("Patient Identity")
    )

    first_power = models.PositiveSmallIntegerField(
        verbose_name=_("Precent of the MT for the first session."),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )

    pulse_type = models.ForeignKey(
        PulseType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Pulse Type"),
    )

    unknown_variable_1 = models.PositiveSmallIntegerField(
        verbose_name=_("unknown_variable_1"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(99)],
    )

    unknown_variable_2 = models.PositiveSmallIntegerField(
        verbose_name=_("unknown_variable_2"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(99)],
    )

    total_sessions = models.PositiveSmallIntegerField(
        verbose_name=_("Total Session Number"),
        null=True,
        validators=[MaxValueValidator(99)],
    )

    total_pulse = models.PositiveIntegerField(
        verbose_name=_("Total Pulse"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(99999)],
    )

    dlpfc_l = models.PositiveSmallIntegerField(
        verbose_name=_("DLPFC Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    dlpfc_r = models.PositiveSmallIntegerField(
        verbose_name=_("DLPFC Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    ofc_l = models.PositiveSmallIntegerField(
        verbose_name=_("OFC Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    ofc_r = models.PositiveSmallIntegerField(
        verbose_name=_("OFC Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    somatosensory_l = models.PositiveSmallIntegerField(
        verbose_name=_("Somatosensory Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    somatosensory_r = models.PositiveSmallIntegerField(
        verbose_name=_("Somatosensory Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    parietal_l = models.PositiveSmallIntegerField(
        verbose_name=_("Parietal Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    parietal_r = models.PositiveSmallIntegerField(
        verbose_name=_("Parietal Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    occipital_l = models.PositiveSmallIntegerField(
        verbose_name=_("Occipital Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    occipital_middle = models.PositiveSmallIntegerField(
        verbose_name=_("Occipital Middle"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    occipital_inf = models.PositiveSmallIntegerField(
        verbose_name=_("Occipital Inferior"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    occipital_r = models.PositiveSmallIntegerField(
        verbose_name=_("Occipital Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    m1_l = models.PositiveSmallIntegerField(
        verbose_name=_("M1 Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    m1_r = models.PositiveSmallIntegerField(
        verbose_name=_("M1 Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    sma_l = models.PositiveSmallIntegerField(
        verbose_name=_("SMA Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    sma_r = models.PositiveSmallIntegerField(
        verbose_name=_("SMA Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    r_post_central = models.PositiveSmallIntegerField(
        verbose_name=_("Right Post Central"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    l_poat_central = models.PositiveSmallIntegerField(
        verbose_name=_("Left Poat Central"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    broca_l = models.PositiveSmallIntegerField(
        verbose_name=_("Broca Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    broca_r = models.PositiveSmallIntegerField(
        verbose_name=_("Broca Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    sub_temporal_r = models.PositiveSmallIntegerField(
        verbose_name=_("Sub Temporal Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    sub_temporal_l = models.PositiveSmallIntegerField(
        verbose_name=_("Sub Temporal Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    middle_temporal_l = models.PositiveSmallIntegerField(
        verbose_name=_("Middle Temporal Left"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )
    middle_temporal_r = models.PositiveSmallIntegerField(
        verbose_name=_("Middle Temporal Right"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )

    def __str__(self):
        return f"RTMS {self.pk} for {self.identity_patient}"

    class Meta:
        verbose_name = _("rTMS")
        verbose_name_plural = _("rTMS")


class Tag(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name=_("Name"))
    name_fa = models.CharField(max_length=255, null=True, verbose_name=_("نام"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class RTMSSession(models.Model):
    identity_patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, verbose_name=_("Patient Identity")
    )
    rtms = models.ForeignKey(RTMS, on_delete=models.CASCADE, verbose_name=_("rTMS"))
    session = models.PositiveSmallIntegerField(
        verbose_name=_("Session Number"), validators=[MaxValueValidator(99)]
    )

    date = models.DateTimeField(verbose_name=_("Session Date and Time"))

    mt = models.PositiveSmallIntegerField(
        verbose_name=_("Motor Threshold"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(999)],
    )

    done = models.BooleanField(verbose_name=_("Done"), default=False)
    power = models.PositiveIntegerField(
        verbose_name=_("Pulse Power"), null=True, blank=True
    )
    note = models.TextField(verbose_name=_("Session Notes"), null=True, blank=True)
    tag = models.ManyToManyField(Tag, verbose_name=_("Tags"), blank=True)

    def __str__(self):
        return f"Session {self.session} for RTMS {self.rtms.pk}"

    class Meta:
        verbose_name = _("RTMS Session")
        verbose_name_plural = _("RTMS Sessions")
