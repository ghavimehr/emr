from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user

        # If user in 'Physicians'
        if user.groups.filter(name='Physicians').exists():
            return '/my_dashboard/'


        # Default fallback
        return '/patients_dashboard/'
