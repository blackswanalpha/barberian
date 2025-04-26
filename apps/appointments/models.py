from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class Appointment(models.Model):
    """
    Model to store appointment bookings.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('pending_review', _('Pending Review')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
        ('no_show', _('No Show')),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_appointments',
        verbose_name=_('Client')
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_appointments',
        verbose_name=_('Staff'),
        null=True,  # Allow null for pending_review appointments
        blank=True  # Allow blank for pending_review appointments
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Service')
    )
    start_time = models.DateTimeField(_('Start time'))
    end_time = models.DateTimeField(_('End time'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('Notes'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['staff']),
            models.Index(fields=['service']),
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.client.first_name} - {self.service.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_past(self):
        return self.start_time < timezone.now()

    @property
    def is_today(self):
        return self.start_time.date() == timezone.now().date()

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now()

    @property
    def duration_minutes(self):
        delta = self.end_time - self.start_time
        return delta.seconds // 60
