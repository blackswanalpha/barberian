from django.urls import path
from . import views_modern

app_name = 'admin_panel'

urlpatterns = [
    # Modern UI URLs
    path('modern/', views_modern.admin_dashboard_modern, name='dashboard_modern'),
    path('modern/appointments/', views_modern.admin_appointments_modern, name='appointments_modern'),
    path('modern/pending-appointments/', views_modern.admin_pending_appointments_modern, name='pending_appointments_modern'),
    path('modern/staff/', views_modern.admin_staff_modern, name='staff_modern'),
    path('modern/services/', views_modern.admin_services_modern, name='services_modern'),

    # Make modern dashboard accessible directly
    path('dashboard-modern/', views_modern.admin_dashboard_modern, name='dashboard_modern_direct'),
]
