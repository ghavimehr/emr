from django.urls import path
from . import views

app_name = "rtms"

urlpatterns = [
    path("", views.rtms_overview, name="rtms_overview"),
]
