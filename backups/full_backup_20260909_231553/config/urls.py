from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Login, Logout, Password reset etc.
    path('accounts/', include('accounts.urls')),             # Your custom app URLs
    path('', include('accounts.urls')),                      # Root redirects to home
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
