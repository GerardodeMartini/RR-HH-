from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Core
    path('admin/', admin.site.urls),

    # Dashboard / Staff Portal
    path('staff/', include('dashboard.urls')),

    # Client / Company Portal
    path('company/', include('clients.urls')),
    
    # Candidate Portal
    path('candidate/', include('candidates.urls')),

    # Main Site (Vacancies List, etc.)
    path('', include('clients.portal_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


