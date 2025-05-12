from django.contrib import admin
from .models import *


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Neurosymp)
class NeurosympAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "domain")
    search_fields = ("name", "domain__name")


@admin.register(CheckNeurosymp)
class CheckNeurosympAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "visit_date", "session_number")
    list_filter = ("visit_date", "session_number")
    search_fields = ("patient__patient_id",)
    # 'data' is a JSON field; you can display or filter on it if needed
