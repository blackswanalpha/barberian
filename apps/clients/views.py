from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import ClientRegistrationForm
from apps.notifications.email_utils import send_welcome_email

def register(request):
    """
    View for client registration.
    """
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Send welcome email
            send_welcome_email(user)

            # Log the user in
            login(request, user)

            # Show success message
            messages.success(request, "Registration successful! Welcome to Barberian.")

            # Redirect to home page
            return redirect('client_portal:home')
    else:
        form = ClientRegistrationForm()

    return render(request, 'clients/register.html', {
        'title': 'Register',
        'form': form
    })
