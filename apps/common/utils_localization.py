from django.utils.translation import get_language
from django.db.models import Model



# for ethnicity and insurance 
def get_localized_name(instance: Model) -> str:
    """
    Function to return the localized name field of a reference model.
    It fetches the correct field like `name_<lang>` or `fname_<lang>` based on current language.
    """

    # Get the current language code
    language_code = get_language()

    # Define a list of possible name fields based on the language code
    field_name = f'name_{language_code}' if hasattr(instance, f'name_{language_code}') else 'name'

    # Check if the field exists on the instance
    if hasattr(instance, field_name):
        return getattr(instance, field_name)
    return None