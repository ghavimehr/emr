from django import forms
from django.utils.translation import gettext_lazy as _
from .models import RTMS, PulseType


class RTMSForm(forms.ModelForm):
    class Meta:
        model = RTMS
        fields = "__all__"
        labels = {
            "identity_patient": _("Patient Identity"),
            "mt": _("MT"),
            "pulse_type": _("Pulse Type"),
            "total_pulse": _("Total Pulse"),
            "dlpfc_l": _("DLPFC Left"),
            "dlpfc_r": _("DLPFC Right"),
            "ofc_l": _("OFC Left"),
            "ofc_r": _("OFC Right"),
            "somatosensory_l": _("Somatosensory Left"),
            "somatosensory_r": _("Somatosensory Right"),
            "parietal_l": _("Parietal Left"),
            "parietal_r": _("Parietal Right"),
            "occipital_l": _("Occipital Left"),
            "occipital_middle": _("Occipital Middle"),
            "occipital_inf": _("Occipital Inferior"),
            "occipital_r": _("Occipital Right"),
            "m1_l": _("M1 Left"),
            "m1_r": _("M1 Right"),
            "sma_l": _("SMA Left"),
            "sma_r": _("SMA Right"),
            "r_post_central": _("Right Post Central"),
            "l_poat_central": _("Left Poat Central"),
            "broca_l": _("Broca Left"),
            "broca_r": _("Broca Right"),
            "sub_temporal_r": _("Sub Temporal Right"),
            "sub_temporal_l": _("Sub Temporal Left"),
            "middle_temporal_l": _("Middle Temporal Left"),
            "middle_temporal_r": _("Middle Temporal Right"),
        }


class PulseTypeForm(forms.ModelForm):
    class Meta:
        model = PulseType
        fields = "__all__"
        labels = {
            "name": _("Name"),
            "name_fa": _("Persian Name"),
        }
