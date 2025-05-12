# ros/admin.py
from django.contrib import admin
from .models import System, Symptom, Ros


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


#    search_fields = ('name')


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "system")
    search_fields = ("name", "system__name")


@admin.register(Ros)
class RosAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "visit_date", "session_number")
    list_filter = ("visit_date", "session_number")
    search_fields = ("patient__patient_id",)
    # 'data' is a JSON field; you can display or filter on it if needed
