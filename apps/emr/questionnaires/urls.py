from django.urls import path
from .views import questionnaire_view

app_name = "questionnaires"

urlpatterns = [
    path(
        "<int:lab_testmeta_id>/",
        questionnaire_view,
        name="questionnaire_<int:lab_testmeta_id>",
    ),
]
