from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import User
from apps.appointments.models import Appointment
from apps.services.models import Service

class Review(models.Model):
    """
    Model for storing client reviews.
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review by {self.client.get_full_name()} for {self.service.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

class ReviewResponse(models.Model):
    """
    Model for storing responses to reviews.
    """
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response to review by {self.review.client.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Review Response')
        verbose_name_plural = _('Review Responses')
