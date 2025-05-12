# identity/admin.py
from django.contrib import admin
from .models import *


@admin.register(Patient)
class IdentityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient_id",
        "first_name",
        "last_name",
        "birthday",
        "ethnicity",
        "marital_status",
        "education_level",
        "blood_group",
        "gender",
        "language_option",
        "phone",
    )
    search_fields = ("id", "patient_id", "first_name", "last_name", "phone")
    filter_horizontal = ("Secretarytags",)


# class InsuranceInline(admin.TabularInline):
#     model = Patient.insurances.through  # Access ManyToMany intermediary model
#     extra = 1  # Number of blank fields to show in admin


@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(BloodGroup)
class BloodGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(LanguageOption)
class LanguageOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(Ethnicity)
class EthnicityAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(DominantHand)
class DominantHandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "name",
        "fname",
    )


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Secretarytags)
class SecretarytagsAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)
