from django.urls import path
from . import views
from . import views_modern
from . import views_user_modern
from . import views_holiday_modern
from . import views_report_modern
from . import views_email
from . import views_auth
from . import views_category_modern

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', views_auth.admin_login, name='admin_login'),
    path('logout/', views_auth.admin_logout, name='admin_logout'),

    # Dashboard
    path('modern/', views.admin_dashboard, name='dashboard'),

    # Users
    path('users/', views.admin_users, name='users'),
    path('users/create/', views_user_modern.admin_user_create_modern, name='user_create'),
    path('users/<int:user_id>/edit/', views_user_modern.admin_user_edit_modern, name='user_edit'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),

    # Business Settings
    path('business-settings/', views.admin_business_settings, name='business_settings'),

    # Business Hours
    path('business-hours/', views.admin_business_hours, name='business_hours'),
    path('business-hours/<int:hour_id>/edit/', views.admin_business_hour_edit, name='business_hour_edit'),

    # Holidays
    path('holidays/', views.admin_holidays, name='holidays'),
    path('holidays/create/', views_holiday_modern.admin_holiday_create_modern, name='holiday_create'),
    path('holidays/<int:holiday_id>/edit/', views_holiday_modern.admin_holiday_edit_modern, name='holiday_edit'),
    path('holidays/<int:holiday_id>/delete/', views.admin_holiday_delete, name='holiday_delete'),

    # Categories
    path('categories/', views.admin_categories, name='categories'),
    path('categories/create/', views_category_modern.admin_category_create_modern, name='category_create'),
    path('categories/<int:category_id>/edit/', views_category_modern.admin_category_edit_modern, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.admin_category_delete, name='category_delete'),

    # Modern Category Pages - Redirects for backward compatibility
    path('categories/create/modern/', views_category_modern.admin_category_create_modern, name='category_create_modern'),
    path('categories/<int:category_id>/edit/modern/', views_category_modern.admin_category_edit_modern, name='category_edit_modern'),

    # Services
    path('services/', views.admin_services, name='services'),
    path('services/create/', views.admin_service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.admin_service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.admin_service_delete, name='service_delete'),

    # Appointments
    path('appointments/', views.admin_appointments, name='appointments'),
    path('appointments/<int:appointment_id>/', views.admin_appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/update/', views.admin_appointment_update, name='appointment_update'),
    path('appointments/<int:appointment_id>/edit/', views.admin_appointment_edit, name='appointment_edit'),
    path('appointments/create/', views.admin_appointment_create, name='appointment_create'),
    path('appointments/<int:appointment_id>/delete/', views.admin_appointment_delete, name='appointment_delete'),
    path('appointments/pending/', views.admin_pending_appointments, name='pending_appointments'),
    path('appointments/<int:appointment_id>/review/', views.admin_review_appointment, name='review_appointment'),
    path('appointments/bulk-assign-staff/', views.admin_bulk_assign_staff, name='bulk_assign_staff'),

    # Modern Pages
    path('appointments/pending/modern/', views_modern.admin_pending_appointments_modern, name='pending_appointments_modern'),
    path('appointments/pending/approve/<int:appointment_id>/', views.admin_approve_appointment, name='approve_appointment'),

    # Modern User Pages - Redirects for backward compatibility
    path('users/create/modern/', views_user_modern.admin_user_create_modern, name='user_create_modern'),
    path('users/<int:user_id>/edit/modern/', views_user_modern.admin_user_edit_modern, name='user_edit_modern'),

    # Modern Staff Pages
    path('staff/create/modern/', views_user_modern.admin_staff_create_modern, name='staff_create_modern'),

    # Modern Holiday Pages
    path('holidays/create/modern/', views_holiday_modern.admin_holiday_create_modern, name='holiday_create_modern'),
    path('holidays/<int:holiday_id>/edit/modern/', views_holiday_modern.admin_holiday_edit_modern, name='holiday_edit_modern'),

    # Modern Report Pages
    path('reports/modern/<int:report_id>/', views_report_modern.admin_report_detail_modern, name='report_detail_modern'),

    # Calendar
    path('calendar/', views.admin_calendar, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.admin_calendar_month, name='calendar_month'),
    path('calendar/week/<int:year>/<int:month>/<int:day>/', views.admin_calendar_week, name='calendar_week'),
    path('calendar/day/<int:year>/<int:month>/<int:day>/', views.admin_day_view, name='day_view'),
    path('appointments/reschedule/', views.admin_appointment_reschedule, name='appointment_reschedule'),

    # Reports
    path('reports/', views.admin_reports, name='reports'),
    path('reports/create/', views_report_modern.admin_report_create_modern, name='report_create'),
    path('reports/<int:report_id>/', views_report_modern.admin_report_detail_modern, name='report_detail'),
    path('reports/<int:report_id>/delete/', views.admin_report_delete, name='report_delete'),

    # Modern Report Pages - Redirects for backward compatibility
    path('reports/create/modern/', views_report_modern.admin_report_create_modern, name='report_create_modern'),

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

    # Email Management
    path('email/', views_email.admin_email_dashboard, name='email_dashboard'),
    path('email/compose/', views_email.admin_email_compose, name='email_compose'),
    path('email/template/create/', views_email.admin_email_template_create, name='email_template_create'),
    path('email/template/<int:template_id>/edit/', views_email.admin_email_template_edit, name='email_template_edit'),
    path('email/template/<int:template_id>/delete/', views_email.admin_email_template_delete, name='email_template_delete'),
    path('email/template/<int:template_id>/get/', views_email.admin_email_template_get, name='email_template_get'),
    path('email/clients/', views_email.admin_email_client_list, name='email_client_list'),
]
