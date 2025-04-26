from django.urls import path
from . import views
from . import views_redesigned

app_name = 'admin_panel'

urlpatterns = [
    # Original URLs
    # ...

    # Redesigned URLs
    path('form-showcase/', views_redesigned.form_showcase, name='form_showcase'),
    path('services/create/redesigned/', views_redesigned.admin_service_create_redesigned, name='service_create_redesigned'),
    path('services/edit/<int:service_id>/redesigned/', views_redesigned.admin_service_edit_redesigned, name='service_edit_redesigned'),
    path('staff/create/redesigned/', views_redesigned.admin_staff_create_redesigned, name='staff_create_redesigned'),
    path('staff/edit/<int:staff_id>/redesigned/', views_redesigned.admin_staff_edit_redesigned, name='staff_edit_redesigned'),
    path('categories/create/redesigned/', views_redesigned.admin_category_create_redesigned, name='category_create_redesigned'),
    path('categories/edit/<int:category_id>/redesigned/', views_redesigned.admin_category_edit_redesigned, name='category_edit_redesigned'),
]
