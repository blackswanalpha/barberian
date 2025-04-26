from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import JSONField
from django.utils.text import slugify

class Report(models.Model):
    """
    Model to store generated reports.
    """
    TYPE_CHOICES = [
        ('appointments', _('Appointments')),
        ('revenue', _('Revenue')),
        ('staff_performance', _('Staff Performance')),
        ('client_activity', _('Client Activity')),
        ('services', _('Services')),
    ]

    name = models.CharField(_('Name'), max_length=100)
    type = models.CharField(_('Type'), max_length=50, choices=TYPE_CHOICES)
    parameters = JSONField(_('Parameters'), blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Created by')
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"

class ReportExport(models.Model):
    """
    Model to store exported report files.
    """
    FORMAT_CHOICES = [
        ('pdf', _('PDF')),
        ('csv', _('CSV')),
        ('xlsx', _('XLSX')),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='exports',
        verbose_name=_('Report')
    )
    file = models.FileField(_('File'), upload_to='reports/')
    format = models.CharField(_('Format'), max_length=10, choices=FORMAT_CHOICES)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Report Export')
        verbose_name_plural = _('Report Exports')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report']),
        ]

    def __str__(self):
        return f"{self.report.name} - {self.get_format_display()}"

class UserLog(models.Model):
    """
    Model to store user activity logs for auditing.
    """
    ACTION_CHOICES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
    ]

    ENTITY_CHOICES = [
        ('appointment', _('Appointment')),
        ('service', _('Service')),
        ('user', _('User')),
        ('category', _('Category')),
        ('report', _('Report')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('User')
    )
    action = models.CharField(_('Action'), max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(_('Entity type'), max_length=50, choices=ENTITY_CHOICES, blank=True, null=True)
    entity_id = models.IntegerField(_('Entity ID'), blank=True, null=True)
    details = JSONField(_('Details'), blank=True, null=True)
    ip_address = models.CharField(_('IP address'), max_length=45, blank=True, null=True)
    user_agent = models.TextField(_('User agent'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('User Log')
        verbose_name_plural = _('User Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.first_name} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EmailTemplate(models.Model):
    """
    Model to store email templates.
    """
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True, blank=True)
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_templates',
        verbose_name=_('Created by')
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
