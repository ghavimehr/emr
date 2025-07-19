# core/management/commands/add_tenant.py
import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from django.contrib.sites.models import Site
from core.models import DatabaseConfig
from core.models import Branding  # if you also want to create a Branding row

class Command(BaseCommand):
    help = "Interactively add a new tenant: DBConfig → migrate → superuser → site"

    def prompt(self, text, default=None):
        if default is not None:
            prompt_text = f"{text} [{default}]: "
        else:
            prompt_text = f"{text}: "
        val = input(prompt_text).strip()
        return val or default

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Add a new tenant ==="))

        # 1) Domain & alias
        domain = self.prompt("Tenant domain (e.g. example.com)")
        if not domain:
            raise CommandError("Domain is required.")
        alias = domain.replace('.', '_')

        # 2) DBConfig defaults from your model
        field_defaults = {
            'db_engine':   DatabaseConfig._meta.get_field('db_engine').default,
            'db_host':     DatabaseConfig._meta.get_field('db_host').default,
            'db_port':     DatabaseConfig._meta.get_field('db_port').default,
            'db_timezone': DatabaseConfig._meta.get_field('db_timezone').default,
        }

        # prompt for each
        engine   = self.prompt("DB ENGINE",   field_defaults['db_engine'])
        name     = self.prompt("DB NAME",     f"{alias}_db")
        user     = self.prompt("DB USER",     f"{alias}_user")
        password = self.prompt("DB PASSWORD", None)
        host     = self.prompt("DB HOST",     field_defaults['db_host'])
        port     = int(self.prompt("DB PORT", field_defaults['db_port']))
        timezone = self.prompt("DB TIMEZONE", field_defaults['db_timezone'])

        # 3) Create or update the DatabaseConfig in customer_config
        cfg, created = DatabaseConfig.using_customer_config().update_or_create(
            name=alias,
            defaults={
                'db_engine':   engine,
                'db_name':     name,
                'db_user':     user,
                'db_password': password,
                'db_host':     host,
                'db_port':     port,
                'db_options':  {"init_command":"SET sql_mode='STRICT_TRANS_TABLES'"},
                'db_timezone': timezone,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ DatabaseConfig for '{alias}' created."))
        else:
            self.stdout.write(self.style.WARNING(f"→ DatabaseConfig for '{alias}' updated."))

        # 4) Register the alias in settings.DATABASES
        if alias not in settings.DATABASES:
            settings.DATABASES[alias] = {
                'ENGINE':            engine,
                'NAME':              name,
                'USER':              user,
                'PASSWORD':          password,
                'HOST':              host,
                'PORT':              port,
                'OPTIONS':           {"init_command":"SET sql_mode='STRICT_TRANS_TABLES'"},
                'TIME_ZONE':         timezone,
                'CONN_MAX_AGE':      0,     # close immediately by default
                'ATOMIC_REQUESTS':   False, # or True if you prefer
                'CONN_HEALTH_CHECKS':True,
                'AUTOCOMMIT':        True,
            }

        # 5) Run migrations on the new tenant
        self.stdout.write(self.style.MIGRATE_LABEL(f"--- Migrating tenant DB '{alias}' ---"))
        call_command('migrate', database=alias, interactive=False)

        # 6) Create a superuser on that DB
        self.stdout.write(self.style.NOTICE(f"--- Create a superuser for '{alias}' ---"))
        call_command('createsuperuser', database=alias)

        # 7) Bootstrap the django_site entry
        site_obj, site_created = Site.objects.update_or_create(
            domain=domain,
            defaults={'name': domain},
        )
        if site_created:
            self.stdout.write(self.style.SUCCESS(f"✓ Site record for '{domain}' created."))
        else:
            self.stdout.write(self.style.WARNING(f"→ Site record for '{domain}' updated."))

        self.stdout.write(self.style.SUCCESS("✅ Tenant setup complete!"))
