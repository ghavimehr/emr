# apps/emr/files/models.py

from django.db import models
from django.contrib.auth.models import Group

class FilePermission(models.Model):
    """
    Defines which PDF-editing permissions each Group has.
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="file_permissions",
    )

    can_view     = models.BooleanField(default=False)
    can_download = models.BooleanField(default=False)
    can_print    = models.BooleanField(default=False)
    can_comment  = models.BooleanField(default=False)
    can_edit     = models.BooleanField(default=False)   # freehand draw/highlight
    can_fill     = models.BooleanField(default=False)   # PDF forms

    class Meta:
        verbose_name = "File Permission by Group"
        verbose_name_plural = "File Permissions by Group"

    def __str__(self):
        return f"{self.group.name}: view={self.can_view}, comment={self.can_comment}, edit={self.can_edit}"

import uuid
from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings


class FileExtension(models.Model):
    """
    Represents a file extension/type (e.g., PDF, DICOM, Text).
    """
    code = models.SlugField(max_length=16, unique=True)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ['code']
        verbose_name = 'File Extension'
        verbose_name_plural = 'File Extensions'

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    """
    Categorizes documents by their subfolder under each patient.
    """
    name = models.CharField(max_length=128)
    name_fa = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    representative_relative_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Subfolder path used to identify this DocumentType"
    )

    def __str__(self):
        return self.name



class PermissionFlag(models.Model):
    """
    Represents a single OnlyOffice permission flag (e.g., view, edit).
    """
    code = models.SlugField(max_length=16, unique=True)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ['code']
        verbose_name = 'Permission Flag'
        verbose_name_plural = 'Permission Flags'

    def __str__(self):
        return self.name


class PermissionProtocol(models.Model):
    """
    A named protocol that maps Django Groups to OnlyOffice permission flags.
    Each protocol defines which PermissionFlags each group has.
    """
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    groups = models.ManyToManyField(
        Group,
        through='ProtocolGroupPermission',
        related_name='permission_protocols'
    )
    # آیتم گروپ طوری نوشته شده است که تمام گروه هایی که
    # برای آنها در مدل زیر پرمیشن تعریف شده است را با نام پروتکل مرتبط کند.
    def get_perms_for_user(self, user):
        """
        Return a dict mapping each PermissionFlag.code to a boolean
        indicating if the user has that permission under this protocol.
        """
        # Initialize all flags to False
        flags = {pf.code: False for pf in PermissionFlag.objects.all()}
        # Fetch all ProtocolGroupPermission entries for user's groups
        qs = ProtocolGroupPermission.objects.filter(
            protocol=self,
            group__in=user.groups.all()
        ).prefetch_related('flags')
        # OR-merge each flag
        for pgp in qs:
            for flag in pgp.flags.all():
                flags[flag.code] = True
        return flags

    def __str__(self):
        return self.name


class ProtocolGroupPermission(models.Model):
    """
    Through-model linking PermissionProtocol to a Django Group
    with a set of PermissionFlags.
    این مدل به تنهایی کاربرد ندارد و در ارتباط با مدل پرمیشن-پرتکل معنا می یابد.
    """
    protocol = models.ForeignKey(
        PermissionProtocol,
        on_delete=models.CASCADE,
        related_name='group_permissions'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='protocol_permissions'
    )
    flags = models.ManyToManyField(
        PermissionFlag,
        related_name='group_permissions'
    )

    class Meta:
        unique_together = ('protocol', 'group')

    def __str__(self):
        return f"{self.protocol.name} - {self.group.name}"


class ProtocolAssignment(models.Model):
    """
    Assigns a default PermissionProtocol to documents whose relative_path
    matches the given Unix-style glob pattern.
    """
    path_pattern = models.CharField(
        max_length=255,
        help_text="fnmatch glob against Document.relative_path"
    )
    protocol = models.ForeignKey(
        PermissionProtocol,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    class Meta:
        ordering = ['path_pattern']

    def __str__(self):
        return f"{self.path_pattern} → {self.protocol.name}"


class Document(models.Model):
    """
    Represents a file in the EMR system. Each document is mapped to one protocol
    at index time to avoid runtime pattern matching.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        'identity.Patient',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    relative_path = models.CharField(
        max_length=255,  # reduced to fit MySQL index limits
        help_text='Path relative to the base data directory, e.g. "12345/reports/scan1.pdf"'
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='documents',
        default=1
    )
    file_name = models.CharField(max_length=255)
    file_extension = models.ForeignKey(
        FileExtension,
        on_delete=models.PROTECT,
        related_name='documents'
    )
    protocol = models.ForeignKey(
        PermissionProtocol,
        on_delete=models.PROTECT,
        related_name='documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'relative_path')
        indexes = [
            models.Index(fields=['patient']),
        ]

    def get_url(self, request):
        rel = reverse('files:serve_patient_file', kwargs={'path': self.relative_path})
        return request.build_absolute_uri(rel)

    def __str__(self):
        return f"{self.patient} – {self.relative_path}"


class DocumentAccessLog(models.Model):
    """
    Logs each time a document is viewed, edited, or saved for auditing.
    """
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('edit', 'Edited'),
        ('save', 'Saved'),
        ('comment', 'Annotated'),
        ('download', 'Downloaded'),
        ('print', 'Printed'),
        ('fill', 'Filled'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    info = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.document} {self.action} by {self.user} at {self.timestamp}"
