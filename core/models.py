# core/models.py

from django.db import models
from django.conf import settings
from django.utils import translation

class Branding(models.Model):
    domain_name          = models.CharField(max_length=255, unique=True)
    doctor_name_en       = models.CharField(max_length=255, blank=True)
    doctor_name_fa       = models.CharField(max_length=255, blank=True)
    doctor_name_short_en = models.CharField(max_length=255, blank=True)
    doctor_name_short_fa = models.CharField(max_length=255, blank=True)
    clinic_name_en       = models.CharField(max_length=255, blank=True)
    clinic_name_fa       = models.CharField(max_length=255, blank=True)
    specialty_en         = models.CharField(max_length=255, blank=True)
    specialty_fa         = models.CharField(max_length=255, blank=True)
    logo_path            = models.CharField(max_length=255)
    language_code        = models.CharField(
                              max_length=2,
                              choices=settings.LANGUAGES,
                              default=settings.LANGUAGE_CODE,
                            )
    hide_designer        = models.BooleanField(default=False, help_text="footer reference to the designer's page")
    slogan1_en           = models.CharField(max_length=255, blank=True, help_text="title of the first page")
    slogan1_fa           = models.CharField(max_length=255, blank=True, help_text="عنوان صفحه اول")

    slogan2_en           = models.CharField(max_length=255, blank=True, help_text="info of the first page")
    slogan2_fa           = models.CharField(max_length=255, blank=True, help_text="توضیح صفحه اول")

    slogan3_en           = models.CharField(max_length=255, blank=True)
    slogan3_fa           = models.CharField(max_length=255, blank=True)

    slogan4_en           = models.CharField(max_length=255, blank=True)
    slogan4_fa           = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table  = 'branding'
        app_label = 'core'

    def __str__(self):
        return self.doctor_name or self.domain_name

    def _get_field(self, field_name):
        # use the *active* language code, not the saved one
        lang = translation.get_language()[:2]    # "fa" or "en"
        val  = getattr(self, f"{field_name}_{lang}")
        if val:
            return val
        # fallback to the other
        other = 'fa' if lang == 'en' else 'en'
        return getattr(self, f"{field_name}_{other}")

    @property
    def doctor_name(self):
        return self._get_field("doctor_name")

    @property
    def clinic_name(self):
        return self._get_field("clinic_name")

    @property
    def specialty(self):
        return self._get_field("specialty")

    @property
    def slogan1(self):
        return self._get_field("slogan1")

    @property
    def slogan2(self):
        return self._get_field("slogan2")

    @property
    def slogan3(self):
        return self._get_field("slogan3")

    @property
    def slogan4(self):
        return self._get_field("slogan14")

    @classmethod
    def using_customer_config(cls):
        return cls.objects.using('customer_config')


class DatabaseConfig(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    db_engine   = models.CharField(max_length=255, default='django.db.backends.mysql')
    db_name     = models.CharField(max_length=255)
    db_user     = models.CharField(max_length=255)
    db_password = models.CharField(max_length=255)
    db_host     = models.CharField(max_length=255, default='127.0.0.1')
    db_port     = models.IntegerField(default=3307)
    db_options  = models.JSONField(default={"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"})
    db_timezone = models.CharField(max_length=100, default="Asia/Tehran")

    class Meta:
        db_table  = 'databaseconfig'
        app_label = 'core'

    def __str__(self):
        return self.name

    @classmethod
    def using_customer_config(cls):
        return cls.objects.using('customer_config')


class OnlyOfficeConfig(models.Model):
    jwt_secret       = models.CharField(max_length=255)
    docserver_url    = models.URLField()
    allowed_ips      = models.JSONField(default=list)
    callback_url     = models.URLField()
    patient_data_path= models.CharField(max_length=255)
    jwt_expire       = models.IntegerField()

    class Meta:
        db_table  = 'onlyofficeconfig'
        app_label = 'core'

    def __str__(self):
        return self.docserver_url

    @classmethod
    def using_customer_config(cls):
        return cls.objects.using('customer_config')


class Connection(models.Model):
    branding         = models.OneToOneField(Branding, on_delete=models.CASCADE)
    default_database = models.ForeignKey(
                           DatabaseConfig,
                           on_delete=models.PROTECT,
                           related_name='connections',
                       )
    onlyoffice       = models.ForeignKey(
                           OnlyOfficeConfig,
                           on_delete=models.PROTECT,
                           related_name='connections',
                       )

    class Meta:
        db_table  = 'connection'
        app_label = 'core'

    def __str__(self):
        return f"Connections for {self.branding.domain_name}"

    @classmethod
    def using_customer_config(cls):
        return cls.objects.using('customer_config')
