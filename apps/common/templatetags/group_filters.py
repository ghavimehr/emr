from django import template
from django.contrib.auth.models import Group


register = template.Library()

@register.filter
def is_in_group(user, groups):
    """
    A custom template filter to check if the user is in any of the specified groups.
    Takes into account the group hierarchy.
    """
    if not user.is_authenticated:
        return False

    # Define the hierarchy of groups
    group_hierarchy = ['Physician', 'Assistant', 'Researcher', 'Secretary']
    
    # Ensure that groups are provided as a list
    user_groups = user.groups.values_list('name', flat=True)

    # Loop through the groups and check if the user is in one of the higher-level groups
    for group in groups:
        if group in group_hierarchy:
            if any(user.groups.filter(name=g).exists() and group_hierarchy.index(group) >= group_hierarchy.index(g) 
                   for g in user.groups.values_list('name', flat=True)):
                return True
    return False