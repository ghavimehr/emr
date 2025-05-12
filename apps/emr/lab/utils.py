# apps/emr/lab/utils.py
import logging
from .models import *
import inspect

logger = logging.getLogger(__name__)


def get_all_test_models():
    """
    Retrieves all test models dynamically using __subclasses__().
    """
    models_list = BaseTest.__subclasses__()
    logger.info(f"Found test models: {[cls.__name__ for cls in models_list]}")
    return models_list


def get_tests_for_category(category_name):
    """
    Returns all test models (classes) whose TestMeta has a matching name (case-insensitive)
    for the given category.
    """
    logger.info(f"Looking for tests in category: {category_name}")
    category = Category.objects.filter(name=category_name).first()
    if not category:
        logger.warning(f"No Category found with name '{category_name}'")
        return []
    test_meta_qs = TestMeta.objects.filter(category=category)
    logger.info(
        f"Found {test_meta_qs.count()} TestMeta rows for category '{category_name}'"
    )
    test_models = {model.__name__.lower(): model for model in get_all_test_models()}
    logger.info(f"Test models dictionary keys: {list(test_models.keys())}")
    tests = []
    for meta in test_meta_qs:
        key = meta.name.lower()
        model = test_models.get(key)
        if model:
            tests.append(model)
            logger.info(
                f"Adding test model '{model.__name__}' for TestMeta with name '{meta.name}'"
            )
        else:
            logger.warning(f"No test model found for TestMeta with name '{meta.name}'")
    logger.info(
        f"Final tests list for category '{category_name}': {[t.__name__ for t in tests]}"
    )
    return tests
