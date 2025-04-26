from django.urls import path
from . import views_updated

app_name = 'admin_panel'

urlpatterns = [
    # Updated URLs with enhanced forms
    path('staff/create/updated/', views_updated.admin_staff_create_updated, name='staff_create_updated'),
    path('staff/edit/<int:staff_id>/updated/', views_updated.admin_staff_edit_updated, name='staff_edit_updated'),
    path('form-showcase-updated/', views_updated.form_showcase_updated, name='form_showcase_updated'),
]
