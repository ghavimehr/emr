from django.contrib import admin
from django.utils.translation import gettext as _
from .models import RTMS, PulseType


@admin.register(PulseType)
class PulseTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "name_fa")
    search_fields = ("name", "name_fa")
    ordering = ("name",)
    # Verbose names for the admin interface will be picked from the model's Meta


@admin.register(RTMS)
class RTMSAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "identity_patient",
        "total_sessions",
        "pulse_type",
        "total_pulse",
    )
    list_filter = ("pulse_type",)
    # Adjust the search_fields lookup for identity_patient if it has a different field (e.g., name)
    search_fields = ("identity_patient__id", "total_pulse")
    ordering = ("id",)
