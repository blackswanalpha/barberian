from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ClientProfile, ClientPreferences, PreferredStaff, PreferredService

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__last_name', 'user__first_name')

@admin.register(ClientPreferences)
class ClientPreferencesAdmin(admin.ModelAdmin):
    list_display = ('client', 'email_notifications', 'sms_notifications', 'reminder_time')
    list_filter = ('email_notifications', 'sms_notifications')
    search_fields = ('client__email', 'client__first_name', 'client__last_name')
    ordering = ('client__last_name', 'client__first_name')

@admin.register(PreferredStaff)
class PreferredStaffAdmin(admin.ModelAdmin):
    list_display = ('client', 'staff', 'created_at')
    search_fields = ('client__email', 'client__first_name', 'client__last_name', 'staff__first_name', 'staff__last_name')
    ordering = ('client__last_name', 'client__first_name')

@admin.register(PreferredService)
class PreferredServiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'created_at')
    search_fields = ('client__email', 'client__first_name', 'client__last_name', 'service__name')
    ordering = ('client__last_name', 'client__first_name')
