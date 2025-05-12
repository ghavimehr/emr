from django.contrib.sites.models import Site
from django.conf import settings

class DynamicDomainMiddleware:
    """
    This middleware dynamically assigns a Site object to the request
    based on the domain in the HTTP Host header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the hostname, removing any port
        host = request.get_host().split(':')[0]
        try:
            # Try to get a matching Site record (case-insensitive)
            site = Site.objects.get(domain__iexact=host)
        except Site.DoesNotExist:
            # Fallback to the default site as defined in SITE_ID
            site = Site.objects.get(pk=settings.SITE_ID)
        # Attach the Site object to the request
        request.site = site
        # Optionally, if you have code that uses get_current_site(request),
        # you can update that call to return request.site.
        response = self.get_response(request)
        return response
