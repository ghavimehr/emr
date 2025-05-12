from django.urls import path
from . import patient_selection, views


urlpatterns = [
    path('', views.welcome_view, name='welcome'),

    path('patient-search/', patient_selection.patient_search, name='patient_search'),
    path('select-patient/', patient_selection.select_patient, name='select_patient'),

    ]
