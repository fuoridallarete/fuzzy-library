# library_project URL Configuration

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
    # Add Django site authentication urls (for login, logout, password management)
    path('accounts/', include('django.contrib.auth.urls')),
    # Add URL maps to redirect the base URL to our application
    path('', RedirectView.as_view(url='library/')),
    # Add URL maps to redirect the base URL to our application
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
