# from django.contrib.auth.decorators import user_passes_test
# from django.contrib import messages
# from django.shortcuts import redirect





# myapp/decorators.py

import functools
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

GROUP_HIERARCHY = ['Secretary', 'Researcher', 'Assistant', 'Physician']

def _user_level(user):
    # gather all the hierarchy‐indices of the groups this user has
    names  = user.groups.values_list('name', flat=True)
    levels = [GROUP_HIERARCHY.index(n)
              for n in names if n in GROUP_HIERARCHY]
    # pick the HIGHEST index (i.e. the most powerful role)
    return max(levels) if levels else None

def has_min_group(user, required_group):
    try:
        req = GROUP_HIERARCHY.index(required_group)
    except ValueError:
        return False
    level = _user_level(user)
    # allow if user’s highest role index ≥ required index
    return level is not None and level >= req

def group_required(required_group, login_url=None, raise_exception=True):
    """
    Only users in `required_group` or any *higher* group can access.
    Authenticated but insufficient → raise 403.
    Not authenticated → redirect to login_url or LOGIN_URL.
    """
    def decorator(view_func):
        @login_required(login_url=login_url)
        @functools.wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not has_min_group(request.user, required_group):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator



# def physician_required(function=None, login_url='/users/signin/'):
#     """
#     A decorator that checks if the logged-in user is in the 'Physician' group.
#     """
#     actual_decorator = user_passes_test(
#         lambda u: u.is_authenticated and u.groups.filter(name='Physicians').exists(),
#         login_url=login_url
#     )
#     return actual_decorator(function) if function else actual_decorator

# def group_required(groups, login_url='/users/signin/'):
#     """
#     A decorator that checks if the logged-in user belongs to any of the specified groups.
#     If a user is part of a higher-level group (e.g., Physician), they should have access
#     to lower-level group areas (e.g., Assistant, Secretary).
#     """
#     def actual_decorator(function=None):
#         def check_group(user):
#             if not user.is_authenticated:
#                 return False

#             # Checking if user is in any of the groups, considering nested access
#             group_hierarchy = ['Physician', 'Assistant', 'Researcher', 'Secretary']
#             for group in groups:
#                 # If user belongs to a group or a higher-level group, grant access
#                 if group_hierarchy.index(group) >= min([group_hierarchy.index(g) for g in user.groups.values_list('name', flat=True)]):
#                     return True

#             return False

#         return user_passes_test(check_group, login_url=login_url)(function) if function else user_passes_test(check_group, login_url=login_url)

#     return actual_decorator


