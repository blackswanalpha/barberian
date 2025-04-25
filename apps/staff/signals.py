from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import StaffSettings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_staff_settings(sender, instance, created, **kwargs):
    """
    Create staff settings when a new user with role 'staff' is created.
    """
    if created and instance.role == 'staff':
        StaffSettings.objects.create(staff=instance)
