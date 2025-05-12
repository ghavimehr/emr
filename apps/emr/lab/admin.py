from django.contrib import admin
from .models import *  # Import all models from the app


class BaseAdmin(admin.ModelAdmin):
    # Dynamically generate list_display based on fields in the BaseTest model
    list_display = ["get_patient", "get_date", "get_tag", "get_registered_event"]

    # Dynamically generate search fields from fields in the BaseTest model
    def get_search_fields(self, request):
        return ["patient__first_name", "patient__last_name", "date"]

    # Dynamically generate list filters from BaseTest model fields
    def get_list_filter(self, request):
        return ["patient", "date", "tag"]

    # Method to display the patient's name (from the related 'patient' field)
    def get_patient(self, obj):
        return obj.patient.first_name if obj.patient else "No Patient"

    # Method to display the test date (from the related 'date' field)
    def get_date(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "No Date"

    # Method to display the tag name (from the related 'tag' field)
    def get_tag(self, obj):
        return obj.tag.name if obj.tag else "No Tag"

    # Method to display the registered event (from the related 'registered_event' field)
    def get_registered_event(self, obj):
        return (
            obj.registered_event.event_type.name if obj.registered_event else "No Event"
        )


# Register models with the admin site using BaseAdmin
model_classes = [
    Category,
    Testtype,
    Tag,
    BloodTestPerformer,
    LpPerformer,
    Psychometrician,
    CBC,
    MetabolicProfile,
    TFT,
    LFT,
    CSF,
    MMSE,
    Moca,
]

for model_class in model_classes:
    admin.site.register(model_class, BaseAdmin)


@admin.register(TestMeta)
class TestMetaAdmin(admin.ModelAdmin):
    pass
