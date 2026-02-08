from django.urls import path
from django.contrib.auth import views as auth_views
from hr_project.views import custom_logout
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.RecruiterLoginView.as_view(), name='dashboard_login'),
    path('logout/', custom_logout, {'next_page': 'dashboard_login'}, name='dashboard_logout'),
    path('board/<int:vacancy_id>/', views.kanban_board, name='kanban_board'),
    
    # AI & Settings
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/analyze/', views.analyze_application_view, name='analyze_application'),
    
    # Candidates List
    path('candidates/', views.candidate_list, name='staff_candidate_list'),
]
