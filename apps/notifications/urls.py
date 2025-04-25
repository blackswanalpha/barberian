from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
]
