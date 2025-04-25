from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Notification(models.Model):
    """
    Model to store notification records sent to users.
    """
    TYPE_CHOICES = [
        ('appointment', _('Appointment')),
        ('reminder', _('Reminder')),
        ('promotion', _('Promotion')),
        ('system', _('System')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )
    type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=100)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Is read'), default=False)
    related_appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='notifications',
        verbose_name=_('Related appointment'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.user.first_name} - {self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class SMSNotification(models.Model):
    """
    Model to store SMS notification records.
    """
    STATUS_CHOICES = [
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('delivered', _('Delivered')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sms_notifications',
        verbose_name=_('User')
    )
    phone_number = models.CharField(_('Phone number'), max_length=20)
    message = models.TextField(_('Message'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES)
    related_appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='sms_notifications',
        verbose_name=_('Related appointment'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('SMS Notification')
        verbose_name_plural = _('SMS Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.first_name} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
