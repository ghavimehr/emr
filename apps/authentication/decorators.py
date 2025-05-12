from django.shortcuts import redirect
from functools import wraps

def role_required(roles):
    """
    Decorator ensuring user is authenticated. Then, if they are in certain
    groups, redirect them to group-specific dashboards. Otherwise, allow
    them to proceed to the original view.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Not logged in => sign in page
                return redirect('/users/signin/')

            user = request.user  # reference request.user directly


            if user.groups.filter(name__in=['Physicians', 'Secretaries', 'Assistants', 'Researchers']).exists():
                return redirect('/my_dashboard/')

            else: # user.groups.filter(name='Patients').exists():
                return redirect('/patients_dashboard/')


            # If user is not in either group => proceed to the view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
