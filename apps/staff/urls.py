from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Staff Dashboard
    path('', views.staff_dashboard, name='dashboard'),

    # Staff Profile
    path('profile/', views.staff_profile, name='profile'),

    # Staff Settings
    path('settings/', views.staff_settings, name='settings'),

    # Staff Schedule
    path('schedule/', views.staff_schedule, name='schedule'),
    path('schedule/<int:schedule_id>/edit/', views.staff_schedule_edit, name='schedule_edit'),

    # Staff Appointments
    path('appointments/', views.staff_appointments, name='appointments'),
    path('appointments/<int:appointment_id>/', views.staff_appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/update/', views.staff_appointment_update, name='appointment_update'),
]
