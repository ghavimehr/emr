# core/templatetags/tenant_static.py

import os
from django import template
from django.templatetags.static import static
from django.contrib.staticfiles import finders

register = template.Library()

@register.simple_tag(takes_context=True)
def tenant_image(context, subpath):
    """
    subpath: e.g. "dist/img/bg-en.png"
    1) split into dir="dist/img" and filename="bg-en.png"
    2) try "dist/img/<brand>-bg-en.png"
    3) else "dist/img/base-bg-en.png"
    4) else fallback to original "dist/img/bg-en.png"
    """
    request = context.get('request')
    brand = None
    if request and getattr(request, 'branding', None):
        # use a slug-safe identifier
        brand = request.branding.domain_name.replace('.', '_')

    dirpath, filename = os.path.split(subpath)

    # build list of candidates in order
    candidates = []
    if brand:
        candidates.append(os.path.join(dirpath, f"{brand}-{filename}"))
    candidates.append(os.path.join(dirpath, f"base-{filename}"))
    candidates.append(subpath)

    for path in candidates:
        # finders.find returns a real filesystem path if it exists
        if finders.find(path):
            # static() will turn it into "/static/…"
            return static(path)

    # ultimate fallback (shouldn't happen if your last candidate is subpath)
    return static(subpath)
