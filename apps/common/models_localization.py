
from django.db.models import ForeignKey, ManyToManyField
from django.db.models import JSONField
from django.apps import apps
from django.utils.translation import get_language
from .utils_localization import get_localized_name

class LocalizedNameMixin:
    def get_localized_field(self, field_name):
        fld = self._meta.get_field(field_name)

        # 1) ForeignKey
        if isinstance(fld, ForeignKey):
            inst = getattr(self, field_name)
            return get_localized_name(inst) if inst else ""

        # 2) ManyToMany
        if isinstance(fld, ManyToManyField):
            return [get_localized_name(i) for i in getattr(self, field_name).all()]

        # 3) JSONField storing {id: flag}
        if isinstance(fld, JSONField):
            data = getattr(self, field_name) or {}
            ids  = [int(k) for k,v in data.items() if v]
            # assume model name = field_name.capitalize()
            Model = apps.get_model(self._meta.app_label, field_name[:-1].capitalize())
            return [get_localized_name(i) for i in Model.objects.filter(pk__in=ids)]

        # fallback
        return getattr(self, field_name)
    
    @property
    def get_localized_name(self):
        return get_localized_name(self)

    def __str__(self):
        # When Django “prints” the instance (in admin, in templates via {{ obj }}, logs, etc.)
        return self.get_localized_name or ""