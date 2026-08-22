from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from clients import views as client_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin Core
    path('admin/', admin.site.urls),
    
    # Auth & Password Reset
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        html_email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Dashboard / Staff Portal
    path('staff/', include('dashboard.urls')),

    # Client / Company Portal
    path('empresas/', include('clients.urls')),
    
    # Candidate Portal
    path('candidates/', include('candidates.urls')),

    # --- Main Site (Vistas Públicas) ---
    path('', client_views.vacancy_list, name='home'),
    path('vacancies/', client_views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', client_views.vacancy_detail, name='vacancy_detail'),
    path('ayuda/', client_views.faq_view, name='faq'),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
