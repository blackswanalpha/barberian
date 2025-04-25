from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import User
from apps.appointments.models import Appointment

class Payment(models.Model):
    """
    Model for storing payment information.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('paypal', _('PayPal')),
        ('cash', _('Cash')),
        ('other', _('Other')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.get_full_name()} - {self.amount}"
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

class PaymentMethod(models.Model):
    """
    Model for storing user payment methods.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    card_expiry_month = models.CharField(max_length=2, blank=True, null=True)
    card_expiry_year = models.CharField(max_length=4, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.payment_type in ['credit_card', 'debit_card']:
            return f"{self.get_payment_type_display()} - {self.card_brand} **** {self.card_last_four}"
        return self.get_payment_type_display()
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')

class Invoice(models.Model):
    """
    Model for storing invoice information.
    """
    INVOICE_STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, related_name='invoice', null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='draft')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount
        
        # Generate invoice number if not provided
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_id = last_invoice.id
            else:
                last_id = 0
            self.invoice_number = f"INV-{self.issue_date.year}{self.issue_date.month:02d}-{last_id + 1:04d}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
