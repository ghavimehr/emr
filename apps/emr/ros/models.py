# ros/models.py

from django.db import models

# For Django 3.1+ with MySQL 5.7+ supporting JSON natively:
from django.db.models import (
    JSONField,
)  # or from django.contrib.postgres.fields import JSONField if using PostgreSQL
from django_jalali.db import models as jmodels


class System(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Symptom(models.Model):
    system = models.ForeignKey(
        System, on_delete=models.CASCADE, related_name="symptoms"
    )
    name = models.CharField(max_length=100)

    # Optionally store a `status` here if you want a default or something else
    # status = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.system.name})"


class Ros(models.Model):
    """
    One row per visit, storing all symptom statuses in a JSON field.
    """

    # Link to your patient model in identity
    patient = models.ForeignKey("identity.Patient", on_delete=models.CASCADE)
    visit_date = jmodels.jDateField()  # models.DateField()
    session_number = models.PositiveIntegerField()

    # A JSON structure { "symptom_id": status, ... }
    data = JSONField(default=dict)

    def __str__(self):
        return f"ROS #{self.id} for {self.patient} on {self.visit_date} (Session {self.session_number})"
