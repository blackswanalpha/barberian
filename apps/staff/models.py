from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.services.models import Service

class StaffSettings(models.Model):
    """
    Model to store settings and preferences for staff members.
    """
    NOTIFICATION_PREFERENCES = [
        ('all', _('All')),
        ('appointments_only', _('Appointments Only')),
        ('important_only', _('Important Only')),
        ('none', _('None')),
    ]

    CALENDAR_VIEW_PREFERENCES = [
        ('day', _('Day')),
        ('week', _('Week')),
        ('month', _('Month')),
    ]

    staff = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_settings',
        verbose_name=_('Staff')
    )
    notification_preference = models.CharField(
        _('Notification preference'),
        max_length=20,
        choices=NOTIFICATION_PREFERENCES,
        default='all'
    )
    email_notifications = models.BooleanField(_('Email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=True)
    auto_confirm_appointments = models.BooleanField(_('Auto confirm appointments'), default=False)
    calendar_view_preference = models.CharField(
        _('Calendar view preference'),
        max_length=10,
        choices=CALENDAR_VIEW_PREFERENCES,
        default='week'
    )
    services = models.ManyToManyField(
        Service,
        verbose_name=_('Services'),
        related_name='staff_settings',
        blank=True
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Staff Settings')
        verbose_name_plural = _('Staff Settings')

    def __str__(self):
        return f"Settings for {self.staff.first_name} {self.staff.last_name}"

class Schedule(models.Model):
    """
    Model to store staff work schedules.
    """
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Staff')
    )
    day_of_week = models.IntegerField(_('Day of week'), choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_('Start time'))
    end_time = models.TimeField(_('End time'))
    is_working = models.BooleanField(_('Is working'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        unique_together = ('staff', 'day_of_week')
        ordering = ['staff', 'day_of_week']

    def __str__(self):
        return f"{self.staff.first_name} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"
