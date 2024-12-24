from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 