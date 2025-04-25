from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """
    Model to store service categories for organizing services.
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True, null=True)
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(_('Is active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    """
    Model to store services offered by the barbershop.
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True, null=True)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    duration = models.IntegerField(_('Duration'), help_text=_('Duration in minutes'))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Category')
    )
    is_active = models.BooleanField(_('Is active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (${self.price})"

class ServiceMedia(models.Model):
    """
    Model to store images and other media related to services.
    """
    MEDIA_TYPES = [
        ('image', _('Image')),
        ('video', _('Video')),
    ]

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name=_('Service')
    )
    media_type = models.CharField(_('Media type'), max_length=20, choices=MEDIA_TYPES, default='image')
    file = models.FileField(_('File'), upload_to='services/')
    is_primary = models.BooleanField(_('Is primary'), default=False)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Service Media')
        verbose_name_plural = _('Service Media')
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.service.name} - {self.get_media_type_display()}"
