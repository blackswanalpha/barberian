from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'staff', 'service', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time')
    search_fields = ('client__email', 'client__first_name', 'client__last_name',
                     'staff__first_name', 'staff__last_name', 'service__name')
    ordering = ('-start_time',)
    date_hierarchy = 'start_time'

    fieldsets = (
        (None, {'fields': ('client', 'staff', 'service')}),
        (_('Schedule'), {'fields': ('start_time', 'end_time')}),
        (_('Status'), {'fields': ('status', 'notes')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['completed', 'no_show']:
            return ('client', 'staff', 'service', 'start_time', 'end_time')
        return ()
