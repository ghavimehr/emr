from django.contrib import admin
from django.contrib.auth.models import Group
from .models import (
    FileExtension,
    PermissionFlag,
    PermissionProtocol,
    ProtocolGroupPermission,
    ProtocolAssignment,
    Document,
    DocumentAccessLog,
)


@admin.register(FileExtension)
class FileExtensionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(PermissionFlag)
class PermissionFlagAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


class ProtocolGroupPermissionInline(admin.TabularInline):
    model = ProtocolGroupPermission
    extra = 1
    verbose_name = 'Group Permission'
    verbose_name_plural = 'Group Permissions'
    filter_horizontal = ('flags',)


@admin.register(PermissionProtocol)
class PermissionProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    inlines = (ProtocolGroupPermissionInline,)


@admin.register(ProtocolGroupPermission)
class ProtocolGroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'group')
    list_filter = ('protocol', 'group')
    search_fields = ('protocol__name', 'group__name')
    filter_horizontal = ('flags',)


@admin.register(ProtocolAssignment)
class ProtocolAssignmentAdmin(admin.ModelAdmin):
    list_display = ('path_pattern', 'protocol')
    list_filter = ('protocol',)
    search_fields = ('path_pattern',)
    ordering = ('path_pattern',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'patient', 'relative_path', 'file_extension', 'protocol',
        'created_at', 'updated_at'
    )
    list_filter = ('file_extension', 'protocol', 'created_at')
    search_fields = ('relative_path', 'patient__id', 'patient__user__username')
    raw_id_fields = ('patient',)
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = (
        'document__relative_path', 'user__username', 'action'
    )
    date_hierarchy = 'timestamp'
