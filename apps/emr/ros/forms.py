# ros/forms.py
from django import forms
from .models import Ros


class RosForm(forms.ModelForm):
    class Meta:
        model = Ros
        fields = ["visit_date", "session_number", "data"]
        # 'data' is a JSONField, so by default, Django would render it as a textarea
