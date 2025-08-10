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
        # 1) if we have a `next` parameter, honor it:
        redirect_to = self.get_redirect_url()   # checks GET/POST for `next`
        if redirect_to:
            return redirect_to

        # 2) otherwise, fall back to your role-based logic:
        user = self.request.user
        if user.is_superuser:
            return '/management/'  # superuser goes to admin management dashboard
        elif user.groups.filter(name__in=['Physicians', 'Researchers', 'Secretaris']).exists() or user.is_staff:
            return '/my_dashboard/'  # any staff role goes to staff dashboard
        elif user.groups.filter(name='patients_costumer').exists():
            return '/patients_dashboard/'  # patient group goes to patient dashboard
        else:
            return '/patients_dashboard/'  # fallback (non-grouped users)

def signout_view(request):
    logout(request)
    return redirect('/')
