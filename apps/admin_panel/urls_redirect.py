from django.urls import path
from . import views_redirect

app_name = 'admin_panel'

urlpatterns = [
    # Redirect to modern dashboard
    path('modern/', views_redirect.redirect_to_modern_dashboard, name='modern_admin'),
]
