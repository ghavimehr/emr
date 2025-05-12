from django_select2.forms import ModelSelect2TagWidget
from django.utils import translation
from .models import Tag


class TagWidget(ModelSelect2TagWidget):
    model = Tag
    search_fields = [
        "name__icontains",
        "fa_name__icontains",
    ]

    def label_from_instance(self, obj):
        current_lang = translation.get_language()
        if current_lang == "fa":
            return obj.fa_name if obj.fa_name else obj.name
        return obj.name

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        # Allow results to appear with 0 typed characters
        kwargs["attrs"].setdefault("data-minimum-input-length", 0)
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        new_values = []
        for val in values:
            if not val.isdigit():
                lang = translation.get_language()
                new_tag = Tag.objects.create(
                    name=val, fa_name=val if lang.startswith("fa") else ""
                )
                new_values.append(str(new_tag.pk))
            else:
                new_values.append(val)
        return new_values

    def get_url(self):
        url = super().get_url()
        # Try to obtain field_id from attributes (either data-field_id or id)
        field_id = self.attrs.get("data-field_id") or self.attrs.get("id", "")
        if field_id and "field_id=" not in url:
            if "?" in url:
                url += "&field_id=" + field_id
            else:
                url += "?field_id=" + field_id
        return url  # Correct: return the local variable 'url'
