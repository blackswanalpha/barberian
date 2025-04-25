from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class ClientProfile(models.Model):
    """
    Model to store additional information for clients.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name=_('User')
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Client Profile')
        verbose_name_plural = _('Client Profiles')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class ClientPreferences(models.Model):
    """
    Model to store client preferences for customizing their experience.
    """
    client = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name=_('Client')
    )
    email_notifications = models.BooleanField(_('Email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=True)
    reminder_time = models.IntegerField(_('Reminder time'), default=24, help_text=_('Hours before appointment'))
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Client Preferences')
        verbose_name_plural = _('Client Preferences')

    def __str__(self):
        return f"Preferences for {self.client.first_name} {self.client.last_name}"

class PreferredStaff(models.Model):
    """
    Model to store client preferences for specific staff members.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferred_staff',
        verbose_name=_('Client')
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferred_by',
        verbose_name=_('Staff')
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Preferred Staff')
        verbose_name_plural = _('Preferred Staff')
        unique_together = ('client', 'staff')

    def __str__(self):
        return f"{self.client.first_name} prefers {self.staff.first_name}"

class PreferredService(models.Model):
    """
    Model to store client preferences for specific services.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferred_services',
        verbose_name=_('Client')
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='preferred_by',
        verbose_name=_('Service')
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Preferred Service')
        verbose_name_plural = _('Preferred Services')
        unique_together = ('client', 'service')

    def __str__(self):
        return f"{self.client.first_name} prefers {self.service.name}"
