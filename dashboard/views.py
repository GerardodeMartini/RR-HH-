from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import views as auth_views
from clients.models import Vacancy
from applications.models import Application
from candidates.models import Candidate

# Check if user is staff/superuser
def is_recruiter(user):
    return user.is_staff

from django.urls import reverse_lazy

class RecruiterLoginView(auth_views.LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard_home')

@login_required
@user_passes_test(is_recruiter)
def dashboard_home(request):
    vacancies = Vacancy.objects.filter(status='active')
    
    # Stats
    total_candidates = Candidate.objects.count()
    active_candidates = Candidate.objects.filter(availability_status='active').count()
    recent_applications = Application.objects.order_by('-applied_at')[:5]

    return render(request, 'dashboard/home.html', {
        'vacancies': vacancies,
        'total_candidates': total_candidates,
        'active_candidates': active_candidates,
        'recent_applications': recent_applications
    })

@login_required
@user_passes_test(is_recruiter)
def kanban_board(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    applications = Application.objects.filter(vacancy=vacancy)
    
    # Stages with Spanish display names
    stage_names = {
        'applied': 'Postulado',
        'initial_interview': 'Entrevista Inicial',
        'tech_evaluation': 'Evaluación Técnica',
        'shortlist': 'Lista Corta / Finalista',
        'offer': 'Oferta Enviada'
    }
    
    kanban_data = {stage: applications.filter(status=stage) for stage in stage_names.keys()}
    
    return render(request, 'dashboard/kanban.html', {
        'vacancy': vacancy,
        'kanban_data': kanban_data,
        'stage_names': stage_names
    })




from utils.gemini_service import analyze_application
from django.http import JsonResponse
from django.contrib import messages

@login_required
@user_passes_test(is_recruiter)
def analyze_application_view(request, application_id):
    if request.method == 'POST':
        result = analyze_application(application_id)
        if result.get('success'):
            messages.success(request, 'Análisis de IA completado.')
        else:
            messages.error(request, f"Error de IA: {result.get('error')}")
            
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_home'))

@login_required
@user_passes_test(is_recruiter)
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    status_choices = Application.STATUS_CHOICES
    return render(request, 'dashboard/application_detail.html', {
        'application': application,
        'status_choices': status_choices
    })

@login_required
@user_passes_test(is_recruiter)
def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(Application, id=application_id)
        new_status = request.POST.get('status')
        if new_status:
            application.status = new_status
            application.save()
            messages.success(request, f'Estado actualizado a: {application.get_status_display()}')
    return redirect('application_detail', application_id=application_id)

@login_required
@user_passes_test(is_recruiter)
def candidate_list(request):
    query = request.GET.get('q', '')
    candidates = Candidate.objects.all().order_by('-user__date_joined')
    
    if query:
        from django.db.models import Q
        candidates = candidates.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(skills__icontains=query)
        )
        
    return render(request, 'dashboard/candidate_list.html', {
        'candidates': candidates,
        'query': query
    })

