from django.contrib import admin
from .models import Meta


@admin.register(Meta)
class MetaAdmin(admin.ModelAdmin):
    pass
