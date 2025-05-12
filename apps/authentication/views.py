from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.views.generic import CreateView
from apps.authentication.forms import SigninForm, SignupForm, UserPasswordChangeForm, UserSetPasswordForm, UserPasswordResetForm
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages

class SignInView(LoginView):
    form_class = SigninForm
    template_name = "authentication/sign-in.html"


    def get_success_url(self):
        user = self.request.user

        # If user is in 'Physicians' group
        if user.groups.filter(name='Physicians').exists():
            return '/my_dashboard/'

        # If user is in 'Patients' group
        elif user.groups.filter(name='Patients').exists():
            return '/patients_dashboard/'

        # Fallback for others
        return '/patients_dashboard/'

def signout_view(request):
    logout(request)
    return redirect('/')
