# apps/emr/oneglance/urls.py

from django.urls import path
from . import views

app_name = "oneglance"

urlpatterns = [
    # path("pdf-by-key/", views.serve_pdf_by_key, name="serve_pdf_by_key"),
    path("", views.oneglance_page, name="oneglance"),
    path("generate_pdf/", views.generate_pdf, name="oneglance_generate_pdf"),
]
