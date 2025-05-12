# apps/emr/events/models.py

from django.db import models
from django.utils import timezone
import pytz
from django.contrib.auth import get_user_model

# Import the Patient model from your identity app.
from apps.emr.identity.models import Patient

# Get the user model from Django's auth system.
User = get_user_model()


def tehran_today():
    """
    Returns today's date in Tehran timezone.
    """
    tehran = pytz.timezone("Asia/Tehran")
    return timezone.now().astimezone(tehran).date()


def tehran_now():
    """
    Returns the current time in Tehran timezone.
    """
    tehran = pytz.timezone("Asia/Tehran")
    return timezone.now().astimezone(tehran).time()


class EventType(models.Model):
    """
    Represents a type of event (e.g., "Appointment", "Follow-up", etc.).
    """

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Event Type (English)"
    )
    fname = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Event Type (Persian)",
    )

    class Meta:
        verbose_name = "Event Type"
        verbose_name_plural = "Event Types"

    def __str__(self):
        # Display the Persian name if available, otherwise the English name.
        return self.fname if self.fname else self.name


class Event(models.Model):
    """
    Records a single event for a patient.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, verbose_name="Patient"
    )
    date = models.DateField(default=tehran_today, verbose_name="Date")
    time = models.TimeField(default=tehran_now, verbose_name="Time")
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, verbose_name="Event Type"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="User"
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"Event for {self.patient} on {self.date} at {self.time}"
