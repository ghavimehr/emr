from django.db import models
from django.db.models import JSONField
from django_jalali.db import models as jmodels


class Domain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fname = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Neurosymp(models.Model):
    domain = models.ForeignKey(
        Domain, on_delete=models.CASCADE, related_name="neurosymps"
    )
    name = models.CharField(max_length=100)
    fname = models.CharField(max_length=100)
    description: models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.domain.name})"


class CheckNeurosymp(models.Model):
    """
    One row per visit, storing all symptom statuses in a JSON field.
    """

    # Link to your patient model in identity
    patient = models.ForeignKey("identity.Patient", on_delete=models.CASCADE)
    visit_date = jmodels.jDateField()  # models.DateField()
    session_number = models.PositiveIntegerField()

    # A JSON structure { "symptom_id": status, ... }
    data = JSONField(default=dict)

    edit_history = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"CHECKNEUROSYMP #{self.id} for {self.patient} on {self.visit_date} (Session {self.session_number})"
