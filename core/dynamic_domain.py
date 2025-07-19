# core/dynamic_domain.py

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from core.models import Branding, Connection
from core.db_routers import set_current_tenant


class DynamicDomainMiddleware(MiddlewareMixin):
    """
    On each request:
    1. Look up Branding by request domain from customer_config.
    2. Pull Connection → DatabaseConfig + OnlyOfficeConfig.
    3. Dynamically register tenant DB under alias.
    4. Set thread‐local for router.
    5. Attach branding & onlyoffice to request.
    """

    def process_request(self, request):
        host = request.get_host().split(':')[0]
        branding_qs = Branding.using_customer_config().filter(domain_name=host)
        branding = branding_qs.first()
        if not branding:
            # let it 404 or fall back
            return

        conn = Connection.using_customer_config() \
                  .select_related('default_database', 'onlyoffice') \
                  .get(branding=branding)

        db = conn.default_database
        # create a safe alias (no dots)
        alias = host.replace('.', '_')

        # register this tenant if not already
        if alias not in settings.DATABASES:
            settings.DATABASES[alias] = {
                'ENGINE':   db.db_engine,
                'NAME':     db.db_name,
                'USER':     db.db_user,
                'PASSWORD': db.db_password,
                'HOST':     db.db_host,
                'PORT':     db.db_port,
                'OPTIONS':  db.db_options,
                'CONN_MAX_AGE':   0,      #How many seconds the Django-database connection can be kept open for reuses.
                'CONN_HEALTH_CHECKS': True,
                'TIME_ZONE': db.db_timezone,
                'ATOMIC_REQUESTS': True,
                'CONN_HEALTH_CHECKS': True,
                'AUTOCOMMIT':        True,
            }

        # tell the router to use this alias
        set_current_tenant(alias)

        # attach to request for later use
        request.branding         = branding
        request.onlyoffice_config= conn.onlyoffice
