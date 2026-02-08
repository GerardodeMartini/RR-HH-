from django.urls import path
from django.contrib.auth import views as auth_views
from hr_project.views import custom_logout
from . import views, portal_views

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    
    # Client Portal
    path('portal/', portal_views.client_portal_home, name='client_portal'),
    path('portal/vacancy/<int:vacancy_id>/', portal_views.client_vacancy_view, name='client_vacancy_view'),
    path('portal/login/', portal_views.CompanyLoginView.as_view(), name='client_login'),
    path('portal/create-vacancy/', portal_views.create_vacancy, name='create_vacancy'),
    path('portal/profile/', portal_views.company_profile, name='company_profile'),
    path('portal/talent-pool/', portal_views.talent_pool, name='talent_pool'),
    # Logout for clients (redirects to login)
    path('portal/logout/', custom_logout, {'next_page': 'client_login'}, name='client_logout'),
]
