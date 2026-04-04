from django.urls import path
from django.contrib.auth import views as auth_views
from hr_project.views import custom_logout
from . import views, portal_views

urlpatterns = [
    # Client Portal (Empresas)
    # The 'empresas/' prefix is added in the project's root urls.py
    path('', portal_views.client_portal_home, name='client_portal'),
    path('vacancy/<int:vacancy_id>/', portal_views.client_vacancy_view, name='client_vacancy_view'),
    path('login/', portal_views.CompanyLoginView.as_view(), name='client_login'),
    path('register/', portal_views.company_register, name='client_register'),
    path('activate/<uidb64>/<token>/', portal_views.activate_company, name='activate_company'),
    path('create-vacancy/', portal_views.create_vacancy, name='create_vacancy'),
    path('profile/', portal_views.company_profile, name='company_profile'),
    # Logout for clients
    path('logout/', custom_logout, {'next_page': 'client_login'}, name='client_logout'),
]
