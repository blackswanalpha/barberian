from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Appointment Booking URLs
    path('booking/service/', views.booking_service, name='booking_service'),
    path('booking/date/', views.booking_date, name='booking_date'),
    path('booking/confirm/', views.booking_confirm, name='booking_confirm'),

    # Calendar Views
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar_month'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_view, name='day_view'),

    # Appointment Management URLs
    path('', views.appointment_list, name='appointment_list'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('<int:appointment_id>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
]
