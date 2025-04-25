from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Notification, SMSNotification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title', 'message')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('user', 'type', 'title', 'message')}),
        (_('Status'), {'fields': ('is_read', 'related_appointment')}),
    )

@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number', 'message')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('user', 'phone_number', 'message')}),
        (_('Status'), {'fields': ('status', 'related_appointment')}),
    )
