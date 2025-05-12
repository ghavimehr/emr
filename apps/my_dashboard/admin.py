from django.contrib import admin
from django.apps import AppConfig

class MyDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.my_dashboard'

