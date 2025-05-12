# apps/emr/events/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .models import Event


@login_required
def event_list(request):
    """
    Displays a list of all events.
    """
    events = Event.objects.all().order_by("-date", "-time")
    context = {
        "events": events,
    }
    return render(request, "emr/events/event_list.html", context)


@login_required
def event_detail(request, event_id):
    """
    Displays a single event in read-only mode.
    """
    event = get_object_or_404(Event, id=event_id)
    context = {
        "event": event,
    }
    return render(request, "emr/events/event_detail_readonly.html", context)
