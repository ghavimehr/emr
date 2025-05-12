from django.urls import path
from apps.patients_dashboard import views

urlpatterns = [
    path('', views.welcome_view, name='patient_dashboard'),
    ]
