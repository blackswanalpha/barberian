from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Review, ReviewResponse

class ReviewForm(forms.ModelForm):
    """
    Form for creating and editing reviews.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
        }
        labels = {
            'rating': _('Rating'),
            'comment': _('Comment'),
        }
        help_texts = {
            'rating': _('Rate your experience from 1 to 5 stars.'),
            'comment': _('Tell us about your experience.'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.choices = [
            (1, '1 - Poor'),
            (2, '2 - Fair'),
            (3, '3 - Good'),
            (4, '4 - Very Good'),
            (5, '5 - Excellent'),
        ]

class ReviewResponseForm(forms.ModelForm):
    """
    Form for creating and editing review responses.
    """
    class Meta:
        model = ReviewResponse
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Respond to this review...'}),
        }
        labels = {
            'response': _('Response'),
        }
        help_texts = {
            'response': _('Your response will be visible to all clients.'),
        }
