from django.urls import re_path, path
from .views import *

app_name = "files"

urlpatterns = [
    path("<uuid:key>/", serve_patient_file, name="serve_patient_file"),
    # re_path(
    #     r'^(?P<path>\d+/.+)$',
    #     serve_patient_file,
    #     name='serve_patient_file',
    # ),
    path(
        "oocallback/",
        onlyoffice_callback,
        name="onlyoffice_callback",
    ),
]
