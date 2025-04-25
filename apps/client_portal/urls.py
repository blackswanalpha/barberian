from django.urls import path
from . import views

app_name = 'client_portal'

urlpatterns = [
    path('', views.splash_screen, name='splash'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services_list, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('staff-list/', views.staff_list, name='staff_list'),
    path('staff-list/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
