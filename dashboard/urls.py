from django.urls import path
from django.contrib.auth import views as auth_views
from hr_project.views import custom_logout
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.RecruiterLoginView.as_view(), name='dashboard_login'),
    path('logout/', custom_logout, {'next_page': 'dashboard_login'}, name='dashboard_logout'),
    path('board/<int:vacancy_id>/', views.kanban_board, name='kanban_board'),
    path('board/<int:vacancy_id>/close/', views.close_vacancy, name='close_vacancy'),
    
    # AI & Settings
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/analyze/', views.analyze_application_view, name='analyze_application'),
    
    # Candidates List
    path('candidates/', views.candidate_list, name='staff_candidate_list'),
    path('candidatos/agregar/', views.add_candidate_view, name='add_candidate'),
    
    # API
    path('api/parse-resume/', views.parse_resume_view, name='api_parse_resume'),
    path('api/check-candidate/', views.check_candidate_exists, name='api_check_candidate'),
]
