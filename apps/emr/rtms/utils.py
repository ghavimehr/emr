import math
from django.apps import apps

from .models import RTMS


def get_rtms_protcols(patient, span_deg=90):
    """
    Collect and shape all rTMS protocol data for a given patient.

    Returns a list of dicts, each with:
      - first_power:        s.first_power
      - power:              s.power
      - unknown_1:          s.unknown_variable_1
      - unknown_2:          s.unknown_variable_2
      - pulse_type:         s.pulse_type or None
      - total_pulse:        s.total_pulse
      - total_sessions:     s.total_sessions
      - areas:              a list of {name, value, angle} for each non-null field
                           other than the excluded fields

    span_deg controls the total fan spread for the area-angle lines.
    """
    # Query all RTMS sessions for this patient, most recent first
    qs = RTMS.objects.filter(identity_patient=patient).order_by('-pk')

    # Fields to skip when building the 'areas' fan
    exclude = {
        'id', 'identity_patient',
        'first_power', 'power', 'pulse_type',
        'unknown_variable_1', 'unknown_variable_2',
        'total_sessions', 'total_pulse',
    }

    protocols = []

    for s in qs:
        # collect (verbose_name, value) for all non-null, non-excluded fields
        raw = []
        for field in s._meta.fields:
            if field.name in exclude:
                continue
            val = getattr(s, field.name)
            if val is not None:
                raw.append((field.verbose_name, val))

        # compute fan angles centered at 0°
        n = len(raw)
        if n <= 1:
            angles = [0]
        else:
            step = span_deg / (n - 1)
            start = -span_deg / 2
            angles = [start + i * step for i in range(n)]

        # build 'areas' entries
        areas = []
        for (name, val), angle in zip(raw, angles):
            areas.append({'name': name, 'value': val, 'angle': angle})

        protocols.append({
            'first_power':    s.first_power,
            'power':          s.power,
            'unknown_1':      s.unknown_variable_1,
            'unknown_2':      s.unknown_variable_2,
            'pulse_type':     s.pulse_type,
            'total_pulse':    s.total_pulse,
            'total_sessions': s.total_sessions,
            'areas':          areas,
        })

    return protocols


