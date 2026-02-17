from django.urls import path
from django.contrib.auth import views as auth_views
from hr_project.views import custom_logout
from . import views, portal_views

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    
    # Client Portal (Empresas)
    path('empresas/', portal_views.client_portal_home, name='client_portal'),
    path('empresas/vacancy/<int:vacancy_id>/', portal_views.client_vacancy_view, name='client_vacancy_view'),
    path('empresas/login/', portal_views.CompanyLoginView.as_view(), name='client_login'),
    path('empresas/register/', portal_views.company_register, name='client_register'),
    path('empresas/create-vacancy/', portal_views.create_vacancy, name='create_vacancy'),
    path('empresas/profile/', portal_views.company_profile, name='company_profile'),
    path('empresas/talent-pool/', portal_views.talent_pool, name='talent_pool'),
    # Logout for clients
    path('empresas/logout/', custom_logout, {'next_page': 'client_login'}, name='client_logout'),
]
