import requests
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from apps.authentication.decorators import role_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

@login_required(login_url='/users/signin/')
def welcome_view(request):
    user = request.user

    # Get user's display name (could be username, first_name, or full name)
    display_name = user.get_full_name() if user.get_full_name() else user.username

    # Check the user's group(s); if you only have one main group per user, you can do:
    groups = user.groups.values_list('name', flat=True)  # e.g. ['Physician', 'Secretary', 'Patient', ...]
    role = ', '.join(groups) if groups else 'No Role'  # or pick the first group

    context = {
        'display_name': display_name,
        'role': role,
        'user_ip': request.META["HTTP_X_REAL_IP"],
    }
    return render(request, 'my_dashboard/welcome.html', context)


