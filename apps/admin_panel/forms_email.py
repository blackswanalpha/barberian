from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.forms.widgets import FileInput

from apps.core.models import User
from .models import EmailTemplate

class MultipleFileInput(FileInput):
    """
    Custom widget to allow multiple file uploads.
    """
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs['multiple'] = True

class EmailForm(forms.Form):
    """
    Form for sending emails to clients.
    """
    recipients = forms.MultipleChoiceField(
        label=_('Recipients'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        required=True,
        help_text=_('Select one or more recipients')
    )

    subject = forms.CharField(
        label=_('Subject'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        required=True
    )

    attachments = forms.FileField(
        label=_('Attachments'),
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        required=False,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'])],
        help_text=_('You can attach multiple files (PDF, DOC, DOCX, JPG, PNG, GIF)')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate recipients choices
        clients = User.objects.filter(role='client').order_by('first_name', 'last_name')
        self.fields['recipients'].choices = [(client.id, f"{client.get_full_name()} ({client.email})") for client in clients]

class EmailTemplateForm(forms.ModelForm):
    """
    Form for creating and editing email templates.
    """
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].help_text = _(
            'You can use the following placeholders: {recipient_name}, {business_name}'
        )
