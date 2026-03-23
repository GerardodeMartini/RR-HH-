from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from clients import portal_views, views as client_views

urlpatterns = [
    # Admin Core
    path('admin/', admin.site.urls),

    # Dashboard / Staff Portal
    path('staff/', include('dashboard.urls')),

    # Client / Company Portal
    path('company/', include('clients.urls')),
    
    # Candidate Portal
    path('candidate/', include('candidates.urls')),

    # --- Main Site (Vistas Públicas) ---
    # Esta es la sección corregida. Ahora apunta directamente a las vistas.
    path('', portal_views.home, name='home'),
    path('vacancies/', portal_views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', client_views.vacancy_detail, name='vacancy_detail'),
    path('application/success/', client_views.application_success, name='application_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
