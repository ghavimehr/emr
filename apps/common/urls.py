from django.urls import path
from . import views

urlpatterns = [
    path('switch-language/<str:lang_code>/', views.switch_language, name='switch-language'),
]
