from django.urls import path
from . import views

# app_name = 'ros'


urlpatterns = [
    path("", views.ros_form_view, name="ros"),
]
