# core/apps.py
# It appends tenants' DB to settings.DATABASES variable so that they can be accessable 


from django.apps import AppConfig
import asyncio
import threading

class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        """
        Preload tenant DB connections. If Django is running under an async event loop (ASGI),
        offload the synchronous ORM calls to a background thread to avoid SynchronousOnlyOperation.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # no event loop; safe to run synchronously
            self._preload_tenants()
            return

        if loop.is_running():
            # running in async context; spawn a thread for ORM calls
            threading.Thread(target=self._preload_tenants, daemon=True).start()
        else:
            # no loop running; safe to call directly
            self._preload_tenants()

    def _preload_tenants(self):
        from django.conf import settings
        from core.models import DatabaseConfig

        for cfg in DatabaseConfig.using_customer_config().all():
            alias = cfg.name
            if alias not in settings.DATABASES:
                settings.DATABASES[alias] = {
                    'ENGINE':            cfg.db_engine,
                    'NAME':              cfg.db_name,
                    'USER':              cfg.db_user,
                    'PASSWORD':          cfg.db_password,
                    'HOST':              cfg.db_host,
                    'PORT':              cfg.db_port,
                    'OPTIONS':           cfg.db_options,
                    'TIME_ZONE':         cfg.db_timezone,
                    'CONN_MAX_AGE':      60,
                    'ATOMIC_REQUESTS':   True,
                    'CONN_HEALTH_CHECKS':True,
                    'AUTOCOMMIT':        True,
                }
