from django.urls import path
from .views import *

app_name = "lab"

urlpatterns = [
    path("", investigations, name="investigations"),
    path("<str:category_name>/", lab_category_view, name="lab_category"),
]
