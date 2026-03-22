from django.urls import path
from .portal_views import home, vacancy_list
from .views import vacancy_detail, application_success

urlpatterns = [
    path('', home, name='home'),
    path('vacancies/', vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', vacancy_detail, name='vacancy_detail'),
    path('application/success/', application_success, name='application_success'),
]
