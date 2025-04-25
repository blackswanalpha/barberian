from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import ClientProfile, ClientPreferences

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Create a client profile when a new user with role 'client' is created.
    """
    if created and instance.role == 'client':
        ClientProfile.objects.create(user=instance)
        ClientPreferences.objects.create(client=instance)
