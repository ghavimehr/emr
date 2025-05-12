# ros/forms.py
from django import forms
from .models import CheckNeurosymp


class RosForm(forms.ModelForm):
    class Meta:
        model = CheckNeurosymp
        fields = ["patient", "visit_date", "session_number", "data"]
        # 'data' is a JSONField, so by default, Django would render it as a textarea

    def save(self, commit=True):
        instance = super().save(commit=False)

        import datetime

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_str = (
            self.request.user.username
            if self.request and self.request.user.is_authenticated
            else "unknown"
        )
        history = instance.edit_history or {}
        history[now_str] = user_str
        instance.edit_history = history

        if commit:
            instance.save()
        return instance
