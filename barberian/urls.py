"""
URL configuration for barberian project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_panel/', include('apps.admin_panel.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('clients/', include('apps.clients.urls')),
    path('staff/', include('apps.staff.urls')),
    path('services/', include('apps.services.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('', include('apps.client_portal.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
