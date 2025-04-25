from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'payments'

urlpatterns = [
    # Default URL - redirect to invoices
    path('', RedirectView.as_view(pattern_name='payments:invoice_list'), name='payments_home'),

    # Payment Processing
    path('process/<int:appointment_id>/', views.payment_process, name='payment_process'),

    # Payment Methods
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/add/', views.payment_method_add, name='payment_method_add'),
    path('methods/<int:method_id>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('methods/<int:method_id>/set-default/', views.payment_method_set_default, name='payment_method_set_default'),

    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
]
