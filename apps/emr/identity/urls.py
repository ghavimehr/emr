from django.urls import path
from . import views

urlpatterns = [
    # List all patients
    path("", views.identity_list, name="identity-list"),
    # Create a new patient
    path("create/", views.identity_create, name="identity-create"),
    # View details of a single patient (pk is the Identity primary key)
    #  path('<int:pk>/', views.identity_detail, name='identity-detail'),
    # Update a patient
    path("<int:pk>/update/", views.identity_update, name="identity-update"),
    # Delete a patient
    path("<int:pk>/delete/", views.identity_delete, name="identity-delete"),
    path(
        "agreement/<int:patient_id>/",
        views.agreement,
        name="agreement",
    ),
    path("occupation-search/", views.occupation_search, name="occupation-search"),
    path(
        "Secretarytags-search/", views.Secretarytags_search, name="Secretarytags-search"
    ),
    path("Secretarytags-add/", views.Secretarytags_add, name="Secretarytags-add"),
]
