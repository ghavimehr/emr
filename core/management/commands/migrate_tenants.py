# core/management/commands/migrate_tenants.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from core.models import DatabaseConfig

class Command(BaseCommand):
    help = 'Run migrations on all or a specific tenant database defined in customer_config'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fake',
            action='store_true',
            dest='fake',
            help='Mark migrations as run without actually running them',
        )
        parser.add_argument(
            '--tenant',
            dest='tenant',
            help='Name of a single tenant to migrate (default: all tenants)',
        )

    def handle(self, *args, **options):
        fake = options.get('fake', False)
        tenant_name = options.get('tenant')

        # Migrate metadata first
        self.stdout.write('Migrating customer_config metadata database...')
        cmd_opts = {'database': 'customer_config', 'interactive': False}
        if fake:
            cmd_opts['fake'] = True
        call_command('migrate', **cmd_opts)

        # Fetch tenant configurations
        qs = DatabaseConfig.using_customer_config().all()
        if tenant_name:
            qs = qs.filter(name=tenant_name)
            if not qs.exists():
                self.stderr.write(self.style.ERROR(f"No tenant named '{tenant_name}' found."))
                return

        # Migrate each tenant
        for cfg in qs:
            alias = cfg.name
            # Dynamically register tenant DB if missing
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

            self.stdout.write(f"--- Migrating tenant: '{alias}' ---")
            cmd_opts = {'database': alias, 'interactive': False}
            if fake:
                cmd_opts['fake'] = True
            call_command('migrate', **cmd_opts)

        self.stdout.write(self.style.SUCCESS('Migrations complete.'))
