from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Report, ReportExport, UserLog

class ReportExportInline(admin.TabularInline):
    model = ReportExport
    extra = 1

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_by', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'created_by__email', 'created_by__first_name', 'created_by__last_name')
    ordering = ('-created_at',)
    inlines = [ReportExportInline]

@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ('report', 'format', 'created_at')
    list_filter = ('format', 'created_at')
    search_fields = ('report__name',)
    ordering = ('-created_at',)

@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'entity_type', 'entity_id', 'ip_address', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'action', 'entity_type', 'entity_id', 'details', 'ip_address', 'user_agent', 'created_at')
