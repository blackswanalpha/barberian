from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import stripe
import uuid

from .models import Payment, PaymentMethod, Invoice
from .forms import PaymentForm, CreditCardForm, PaymentMethodForm
from apps.appointments.models import Appointment
from apps.notifications.models import Notification

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_process(request, appointment_id):
    """
    Process payment for an appointment.
    """
    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user is the client
    if request.user != appointment.client:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')
    
    # Check if the appointment is already paid
    if hasattr(appointment, 'payment') and appointment.payment.status == 'completed':
        messages.info(request, "This appointment has already been paid.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    # Get the user's saved payment methods
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    # Initialize forms
    payment_form = PaymentForm(request.POST or None)
    credit_card_form = CreditCardForm(request.POST or None)
    
    if request.method == 'POST' and payment_form.is_valid():
        payment_method = payment_form.cleaned_data['payment_method']
        
        # Process payment based on the selected method
        if payment_method in ['credit_card', 'debit_card']:
            # Process credit/debit card payment
            if credit_card_form.is_valid():
                try:
                    # Create a payment token with Stripe
                    token = stripe.Token.create(
                        card={
                            'number': credit_card_form.cleaned_data['card_number'],
                            'exp_month': credit_card_form.cleaned_data['card_expiry_month'],
                            'exp_year': credit_card_form.cleaned_data['card_expiry_year'],
                            'cvc': credit_card_form.cleaned_data['card_cvc'],
                        },
                    )
                    
                    # Create a charge
                    charge = stripe.Charge.create(
                        amount=int(appointment.service.price * 100),  # Amount in cents
                        currency='usd',
                        source=token.id,
                        description=f'Payment for {appointment.service.name} appointment',
                        metadata={
                            'appointment_id': appointment.id,
                            'client_id': request.user.id,
                            'client_name': request.user.get_full_name(),
                            'service': appointment.service.name,
                        }
                    )
                    
                    # Save the payment
                    payment = Payment.objects.create(
                        user=request.user,
                        appointment=appointment,
                        amount=appointment.service.price,
                        status='completed',
                        payment_method=payment_method,
                        transaction_id=charge.id,
                        notes=payment_form.cleaned_data.get('notes', '')
                    )
                    
                    # Save the card for future payments if requested
                    if credit_card_form.cleaned_data.get('save_card'):
                        # Get the card details from the token
                        card = charge.source
                        
                        # Save the payment method
                        PaymentMethod.objects.create(
                            user=request.user,
                            payment_type=payment_method,
                            card_last_four=card.last4,
                            card_brand=card.brand,
                            card_expiry_month=card.exp_month,
                            card_expiry_year=card.exp_year,
                            is_default=not payment_methods.exists()  # Set as default if no other methods exist
                        )
                    
                    # Create an invoice
                    due_date = timezone.now().date() + timedelta(days=30)
                    Invoice.objects.create(
                        user=request.user,
                        appointment=appointment,
                        payment=payment,
                        amount=appointment.service.price,
                        tax_amount=0,  # No tax for now
                        total_amount=appointment.service.price,
                        status='paid',
                        due_date=due_date
                    )
                    
                    # Create a notification
                    Notification.objects.create(
                        user=request.user,
                        type='payment',
                        title='Payment Successful',
                        message=f"Your payment of ${appointment.service.price} for {appointment.service.name} has been processed successfully.",
                        related_appointment=appointment
                    )
                    
                    # Show a success message
                    messages.success(request, "Payment processed successfully.")
                    
                    # Redirect to the appointment detail page
                    return redirect('appointments:appointment_detail', appointment_id=appointment.id)
                
                except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    body = e.json_body
                    err = body.get('error', {})
                    messages.error(request, f"Card error: {err.get('message')}")
                
                except stripe.error.RateLimitError:
                    # Too many requests made to the API too quickly
                    messages.error(request, "Rate limit error. Please try again later.")
                
                except stripe.error.InvalidRequestError:
                    # Invalid parameters were supplied to Stripe's API
                    messages.error(request, "Invalid request. Please check your card details.")
                
                except stripe.error.AuthenticationError:
                    # Authentication with Stripe's API failed
                    messages.error(request, "Authentication error. Please contact support.")
                
                except stripe.error.APIConnectionError:
                    # Network communication with Stripe failed
                    messages.error(request, "Network error. Please try again later.")
                
                except stripe.error.StripeError:
                    # Display a very generic error to the user
                    messages.error(request, "Something went wrong. Please try again later.")
                
                except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    messages.error(request, f"An error occurred: {str(e)}")
        
        elif payment_method == 'paypal':
            # For now, just simulate a PayPal payment
            # In a real application, you would integrate with PayPal's API
            
            # Save the payment
            payment = Payment.objects.create(
                user=request.user,
                appointment=appointment,
                amount=appointment.service.price,
                status='completed',
                payment_method=payment_method,
                transaction_id=f'PAYPAL-{uuid.uuid4().hex[:10].upper()}',
                notes=payment_form.cleaned_data.get('notes', '')
            )
            
            # Create an invoice
            due_date = timezone.now().date() + timedelta(days=30)
            Invoice.objects.create(
                user=request.user,
                appointment=appointment,
                payment=payment,
                amount=appointment.service.price,
                tax_amount=0,  # No tax for now
                total_amount=appointment.service.price,
                status='paid',
                due_date=due_date
            )
            
            # Create a notification
            Notification.objects.create(
                user=request.user,
                type='payment',
                title='Payment Successful',
                message=f"Your payment of ${appointment.service.price} for {appointment.service.name} has been processed successfully.",
                related_appointment=appointment
            )
            
            # Show a success message
            messages.success(request, "Payment processed successfully via PayPal.")
            
            # Redirect to the appointment detail page
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
        
        elif payment_method == 'cash':
            # For cash payments, mark as pending until paid in person
            
            # Save the payment
            payment = Payment.objects.create(
                user=request.user,
                appointment=appointment,
                amount=appointment.service.price,
                status='pending',
                payment_method=payment_method,
                notes=payment_form.cleaned_data.get('notes', '')
            )
            
            # Create an invoice
            due_date = timezone.now().date() + timedelta(days=30)
            Invoice.objects.create(
                user=request.user,
                appointment=appointment,
                payment=payment,
                amount=appointment.service.price,
                tax_amount=0,  # No tax for now
                total_amount=appointment.service.price,
                status='sent',
                due_date=due_date
            )
            
            # Create a notification
            Notification.objects.create(
                user=request.user,
                type='payment',
                title='Cash Payment Selected',
                message=f"You have selected to pay ${appointment.service.price} for {appointment.service.name} in cash. Please pay at the time of your appointment.",
                related_appointment=appointment
            )
            
            # Show a success message
            messages.success(request, "Cash payment option selected. Please pay at the time of your appointment.")
            
            # Redirect to the appointment detail page
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    return render(request, 'payments/payment_process.html', {
        'title': 'Process Payment',
        'appointment': appointment,
        'payment_form': payment_form,
        'credit_card_form': credit_card_form,
        'payment_methods': payment_methods,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def payment_methods(request):
    """
    View for managing payment methods.
    """
    # Get the user's payment methods
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    return render(request, 'payments/payment_methods.html', {
        'title': 'Payment Methods',
        'payment_methods': payment_methods
    })

@login_required
def payment_method_add(request):
    """
    View for adding a new payment method.
    """
    # Initialize forms
    payment_method_form = PaymentMethodForm(request.POST or None)
    credit_card_form = CreditCardForm(request.POST or None)
    
    if request.method == 'POST' and payment_method_form.is_valid():
        payment_type = payment_method_form.cleaned_data['payment_type']
        is_default = payment_method_form.cleaned_data['is_default']
        
        if payment_type in ['credit_card', 'debit_card']:
            # Process credit/debit card
            if credit_card_form.is_valid():
                try:
                    # Create a payment token with Stripe
                    token = stripe.Token.create(
                        card={
                            'number': credit_card_form.cleaned_data['card_number'],
                            'exp_month': credit_card_form.cleaned_data['card_expiry_month'],
                            'exp_year': credit_card_form.cleaned_data['card_expiry_year'],
                            'cvc': credit_card_form.cleaned_data['card_cvc'],
                        },
                    )
                    
                    # Get the card details from the token
                    card = token.card
                    
                    # If this is the default payment method, set all others to non-default
                    if is_default:
                        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
                    
                    # Save the payment method
                    PaymentMethod.objects.create(
                        user=request.user,
                        payment_type=payment_type,
                        card_last_four=card.last4,
                        card_brand=card.brand,
                        card_expiry_month=card.exp_month,
                        card_expiry_year=card.exp_year,
                        is_default=is_default
                    )
                    
                    # Show a success message
                    messages.success(request, "Payment method added successfully.")
                    
                    # Redirect to the payment methods page
                    return redirect('payments:payment_methods')
                
                except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    body = e.json_body
                    err = body.get('error', {})
                    messages.error(request, f"Card error: {err.get('message')}")
                
                except Exception as e:
                    # Something else happened
                    messages.error(request, f"An error occurred: {str(e)}")
        
        else:
            # For other payment types (e.g., PayPal, Cash)
            # If this is the default payment method, set all others to non-default
            if is_default:
                PaymentMethod.objects.filter(user=request.user).update(is_default=False)
            
            # Save the payment method
            PaymentMethod.objects.create(
                user=request.user,
                payment_type=payment_type,
                is_default=is_default
            )
            
            # Show a success message
            messages.success(request, "Payment method added successfully.")
            
            # Redirect to the payment methods page
            return redirect('payments:payment_methods')
    
    return render(request, 'payments/payment_method_form.html', {
        'title': 'Add Payment Method',
        'payment_method_form': payment_method_form,
        'credit_card_form': credit_card_form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def payment_method_delete(request, method_id):
    """
    View for deleting a payment method.
    """
    # Get the payment method
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    if request.method == 'POST':
        # Check if this is the default payment method
        is_default = payment_method.is_default
        
        # Delete the payment method
        payment_method.delete()
        
        # If this was the default payment method, set another one as default
        if is_default:
            other_method = PaymentMethod.objects.filter(user=request.user).first()
            if other_method:
                other_method.is_default = True
                other_method.save()
        
        # Show a success message
        messages.success(request, "Payment method deleted successfully.")
        
        # Redirect to the payment methods page
        return redirect('payments:payment_methods')
    
    return render(request, 'payments/payment_method_delete.html', {
        'title': 'Delete Payment Method',
        'payment_method': payment_method
    })

@login_required
def payment_method_set_default(request, method_id):
    """
    View for setting a payment method as default.
    """
    # Get the payment method
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    # Set all payment methods to non-default
    PaymentMethod.objects.filter(user=request.user).update(is_default=False)
    
    # Set this payment method as default
    payment_method.is_default = True
    payment_method.save()
    
    # Show a success message
    messages.success(request, "Default payment method updated successfully.")
    
    # Redirect to the payment methods page
    return redirect('payments:payment_methods')

@login_required
def invoice_list(request):
    """
    View for listing invoices.
    """
    # Get the user's invoices
    if request.user.role == 'client':
        invoices = Invoice.objects.filter(user=request.user)
    elif request.user.role in ['staff', 'admin']:
        invoices = Invoice.objects.all()
    else:
        invoices = Invoice.objects.none()
    
    return render(request, 'payments/invoice_list.html', {
        'title': 'Invoices',
        'invoices': invoices
    })

@login_required
def invoice_detail(request, invoice_id):
    """
    View for viewing invoice details.
    """
    # Get the invoice
    if request.user.role == 'client':
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    elif request.user.role in ['staff', 'admin']:
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')
    
    return render(request, 'payments/invoice_detail.html', {
        'title': 'Invoice Details',
        'invoice': invoice
    })
