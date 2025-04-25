from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Public review views
    path('', views.review_list, name='review_list'),
    path('<int:review_id>/', views.review_detail, name='review_detail'),
    
    # Client review management
    path('create/', views.review_create, name='review_create'),
    path('create/<int:appointment_id>/', views.review_create, name='review_create_appointment'),
    path('<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    
    # Staff and service reviews
    path('staff/<int:staff_id>/', views.staff_reviews, name='staff_reviews'),
    path('staff/', views.staff_reviews, name='my_staff_reviews'),
    path('service/<int:service_id>/', views.service_reviews, name='service_reviews'),
    
    # Admin review management
    path('admin/', views.admin_review_list, name='admin_review_list'),
    path('admin/<int:review_id>/approve/', views.admin_review_approve, name='admin_review_approve'),
]
