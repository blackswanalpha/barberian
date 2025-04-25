from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),

    # Users
    path('users/', views.admin_users, name='users'),
    path('users/create/', views.admin_user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),

    # Business Settings
    path('business-settings/', views.admin_business_settings, name='business_settings'),

    # Business Hours
    path('business-hours/', views.admin_business_hours, name='business_hours'),
    path('business-hours/<int:hour_id>/edit/', views.admin_business_hour_edit, name='business_hour_edit'),

    # Holidays
    path('holidays/', views.admin_holidays, name='holidays'),
    path('holidays/create/', views.admin_holiday_create, name='holiday_create'),
    path('holidays/<int:holiday_id>/edit/', views.admin_holiday_edit, name='holiday_edit'),
    path('holidays/<int:holiday_id>/delete/', views.admin_holiday_delete, name='holiday_delete'),

    # Categories
    path('categories/', views.admin_categories, name='categories'),
    path('categories/create/', views.admin_category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.admin_category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.admin_category_delete, name='category_delete'),

    # Services
    path('services/', views.admin_services, name='services'),
    path('services/create/', views.admin_service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.admin_service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.admin_service_delete, name='service_delete'),

    # Appointments
    path('appointments/', views.admin_appointments, name='appointments'),
    path('appointments/<int:appointment_id>/', views.admin_appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/update/', views.admin_appointment_update, name='appointment_update'),
    path('appointments/create/', views.admin_appointment_create, name='appointment_create'),

    # Calendar
    path('calendar/', views.admin_calendar, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.admin_calendar_month, name='calendar_month'),
    path('calendar/week/<int:year>/<int:month>/<int:day>/', views.admin_calendar_week, name='calendar_week'),
    path('calendar/day/<int:year>/<int:month>/<int:day>/', views.admin_day_view, name='day_view'),
    path('appointments/reschedule/', views.admin_appointment_reschedule, name='appointment_reschedule'),

    # Reports
    path('reports/', views.admin_reports, name='reports'),
    path('reports/create/', views.admin_report_create, name='report_create'),
    path('reports/<int:report_id>/', views.admin_report_detail, name='report_detail'),
    path('reports/<int:report_id>/delete/', views.admin_report_delete, name='report_delete'),

    # Reviews
    path('reviews/', views.admin_reviews, name='reviews'),

    # Staff Management
    path('staff/', views.admin_staff, name='staff'),
    path('staff/create/', views.admin_staff_create, name='staff_create'),
    path('staff/<int:staff_id>/edit/', views.admin_staff_edit, name='staff_edit'),
    path('staff/<int:staff_id>/delete/', views.admin_staff_delete, name='staff_delete'),
    path('staff/schedule/', views.admin_staff_schedule, name='staff_schedule'),
    path('staff/<int:staff_id>/schedule/save/', views.admin_staff_schedule_save, name='staff_schedule_save'),
    path('staff/<int:staff_id>/timeoff/add/', views.admin_staff_timeoff_add, name='staff_timeoff_add'),
    path('staff/timeoff/<int:timeoff_id>/edit/', views.admin_staff_timeoff_edit, name='staff_timeoff_edit'),
    path('staff/timeoff/<int:timeoff_id>/delete/', views.admin_staff_timeoff_delete, name='staff_timeoff_delete'),
    path('staff/performance/', views.admin_staff_performance, name='staff_performance'),

    # Media Management
    path('media/', views.admin_media, name='media'),
    path('media/gallery/', views.admin_media_gallery, name='media_gallery'),
    path('media/upload/', views.admin_media_upload, name='media_upload'),
    path('media/upload-modal/', views.admin_media_upload_modal, name='media_upload_modal'),
    path('media/<int:media_id>/delete/', views.admin_media_delete, name='media_delete'),
    path('media/<int:media_id>/set-primary/', views.admin_media_set_primary, name='media_set_primary'),
    path('media/<int:media_id>/edit/', views.admin_media_edit, name='media_edit'),
    path('media/<int:media_id>/edit/save/', views.admin_media_edit_save, name='media_edit_save'),

    # Logs
    path('logs/', views.admin_logs, name='logs'),
]
