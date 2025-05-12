from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect


def physician_required(function=None, login_url='/users/signin/'):
    """
    A decorator that checks if the logged-in user is in the 'Physician' group.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name='Physicians').exists(),
        login_url=login_url
    )
    return actual_decorator(function) if function else actual_decorator

def group_required(groups, login_url='/users/signin/'):
    """
    A decorator that checks if the logged-in user belongs to any of the specified groups.
    If a user is part of a higher-level group (e.g., Physician), they should have access
    to lower-level group areas (e.g., Assistant, Secretary).
    """
    def actual_decorator(function=None):
        def check_group(user):
            if not user.is_authenticated:
                return False

            # Checking if user is in any of the groups, considering nested access
            group_hierarchy = ['Physician', 'Assistant', 'Researcher', 'Secretary']
            for group in groups:
                # If user belongs to a group or a higher-level group, grant access
                if group_hierarchy.index(group) >= min([group_hierarchy.index(g) for g in user.groups.values_list('name', flat=True)]):
                    return True

            return False

        return user_passes_test(check_group, login_url=login_url)(function) if function else user_passes_test(check_group, login_url=login_url)

    return actual_decorator


