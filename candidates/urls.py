from django.urls import path
from . import views

urlpatterns = [
    path('update/<uuid:token>/', views.quick_update_view, name='quick_update'),
    
    # Portal Auth
    path('login/', views.candidate_login, name='candidate_login'),
    path('register/', views.candidate_register, name='candidate_register'),
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
]
