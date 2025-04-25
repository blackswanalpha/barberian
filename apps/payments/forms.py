from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Payment, PaymentMethod

class PaymentForm(forms.ModelForm):
    """
    Form for processing payments.
    """
    class Meta:
        model = Payment
        fields = ['payment_method', 'notes']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CreditCardForm(forms.Form):
    """
    Form for credit card details.
    """
    card_number = forms.CharField(
        label=_('Card Number'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '•••• •••• •••• ••••',
            'autocomplete': 'cc-number',
            'data-stripe': 'number'
        })
    )
    card_expiry_month = forms.ChoiceField(
        label=_('Expiry Month'),
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-stripe': 'exp-month'
        })
    )
    card_expiry_year = forms.ChoiceField(
        label=_('Expiry Year'),
        choices=[(str(i), str(i)) for i in range(2023, 2036)],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-stripe': 'exp-year'
        })
    )
    card_cvc = forms.CharField(
        label=_('CVC'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '•••',
            'autocomplete': 'cc-csc',
            'data-stripe': 'cvc'
        })
    )
    save_card = forms.BooleanField(
        label=_('Save card for future payments'),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        # Remove spaces and dashes
        card_number = card_number.replace(' ', '').replace('-', '')
        
        # Check if the card number is valid (simple check)
        if not card_number.isdigit():
            raise forms.ValidationError(_('Card number must contain only digits.'))
        
        if len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError(_('Card number must be between 13 and 19 digits.'))
        
        return card_number
    
    def clean_card_cvc(self):
        card_cvc = self.cleaned_data.get('card_cvc')
        
        # Check if the CVC is valid
        if not card_cvc.isdigit():
            raise forms.ValidationError(_('CVC must contain only digits.'))
        
        if len(card_cvc) < 3 or len(card_cvc) > 4:
            raise forms.ValidationError(_('CVC must be 3 or 4 digits.'))
        
        return card_cvc

class PaymentMethodForm(forms.ModelForm):
    """
    Form for managing payment methods.
    """
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'is_default']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
