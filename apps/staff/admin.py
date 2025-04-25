from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import StaffSettings, Schedule

# Removed ScheduleInline as it's not needed

@admin.register(StaffSettings)
class StaffSettingsAdmin(admin.ModelAdmin):
    list_display = ('staff', 'notification_preference', 'email_notifications', 'sms_notifications', 'auto_confirm_appointments')
    list_filter = ('notification_preference', 'email_notifications', 'sms_notifications', 'auto_confirm_appointments')
    search_fields = ('staff__email', 'staff__first_name', 'staff__last_name')
    ordering = ('staff__last_name', 'staff__first_name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'get_day_of_week_display', 'start_time', 'end_time', 'is_working')
    list_filter = ('day_of_week', 'is_working')
    search_fields = ('staff__email', 'staff__first_name', 'staff__last_name')
    ordering = ('staff__last_name', 'staff__first_name', 'day_of_week')
