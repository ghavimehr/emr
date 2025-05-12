from django.urls import path
from . import views


urlpatterns = [
    path("", views.ros_form_view, name="checkneurosymp"),
]
