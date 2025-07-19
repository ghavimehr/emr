# core/db_routers.py

import threading

_thread_locals = threading.local()

def set_current_tenant(alias: str):
    _thread_locals.tenant_alias = alias

def get_current_tenant() -> str:
    return getattr(_thread_locals, 'tenant_alias', None)


class TenantRouter:
    """
    - core app models (branding, db, onlyoffice, connection) → customer_config
    - all other models → current tenant DB (set in middleware)
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'core':
            return 'customer_config'
        return get_current_tenant() or 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'core':
            return 'customer_config'
        return get_current_tenant() or 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # allow relations only within same DB
        db1 = obj1._state.db
        db2 = obj2._state.db
        if db1 == db2:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # core app → only on customer_config
        if app_label == 'core':
            return db == 'customer_config'
        # all other apps → never on customer_config
        if db == 'customer_config':
            return False
        # allow normal migrations on tenant & default
        return True
