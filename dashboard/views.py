from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import views as auth_views
from clients.models import Vacancy
from applications.models import Application
from candidates.models import Candidate
from django.conf import settings

# Check if user is staff/superuser
def is_recruiter(user):
    return user.is_staff

from django.urls import reverse_lazy

from django.contrib import messages
from utils.turnstile import validate_turnstile

class RecruiterLoginView(auth_views.LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard_home')

    def post(self, request, *args, **kwargs):
        turnstile_result = validate_turnstile(request)
        if not turnstile_result.get('success'):
            messages.error(request, 'Error de verificación de seguridad (Captcha). Por favor, intenta de nuevo.')
            return render(request, self.template_name, {'form': self.get_form()})
            
        return super().post(request, *args, **kwargs)
        
from candidates.forms import CandidateProfileForm

@login_required
@user_passes_test(is_recruiter)
def add_candidate_view(request):
    if request.method == 'POST':
        # Check if we are updating an existing candidate
        existing_id = request.POST.get('existing_candidate_id')
        instance = None
        if existing_id:
            instance = get_object_or_404(Candidate, id=existing_id)
            
        form = CandidateProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            candidate = form.save(commit=False)
            # No user associated for manual entry
            candidate.save()
            form.save_m2m() # For tags if any
            
            try:
                from utils.document_converter import ensure_pdf_resume
                ensure_pdf_resume(candidate)
            except ImportError:
                pass
            
            action_msg = 'actualizado' if instance else 'agregado'
            messages.success(request, f'Candidato {action_msg} correctamente.')
            return redirect('staff_candidate_list')
    else:
        form = CandidateProfileForm()
    
    return render(request, 'dashboard/add_candidate.html', {'form': form})

@login_required
@user_passes_test(is_recruiter)
def check_candidate_exists(request):
    email_input = request.GET.get('email', '').strip()
    first_name = request.GET.get('first_name', '').strip()
    last_name = request.GET.get('last_name', '').strip()
    
    matches = []
    
    # Split input emails
    emails_to_check = [e.strip() for e in email_input.split(',') if e.strip()]
    
    if emails_to_check:
        from django.db.models import Q
        # Check if ANY of the input emails match ANY stored email (primary or secondary)
        for email in emails_to_check:
            # Check against primary email
            by_email = Candidate.objects.filter(email__iexact=email).first()
            if by_email:
                matches.append({
                    'id': by_email.id,
                    'name': f"{by_email.first_name} {by_email.last_name}",
                    'email': by_email.email,
                    'reason': f'Email coincidente: {email}'
                })
                continue # Found one, move to next input email (though usually one match is enough to alert)
            
            # Check against secondary email (contains string)
            # This is a bit looser, "secondary_email__icontains" might match substrings.
            # Ideally we'd split the stored secondary email too, but for a quick check containment is okay-ish 
            # if we assume standard format. Better: regex or strict check requires iterating.
            # Let's use icontains for now as a "possible match" warning.
            by_sec_email = Candidate.objects.filter(secondary_email__icontains=email).first()
            if by_sec_email:
                 matches.append({
                    'id': by_sec_email.id,
                    'name': f"{by_sec_email.first_name} {by_sec_email.last_name}",
                    'email': by_sec_email.email,
                    'reason': f'Email secundario coincidente: {email}'
                })
            
    if first_name and last_name:
        by_name = Candidate.objects.filter(
            first_name__iexact=first_name, 
            last_name__iexact=last_name
        ).exclude(email__iexact=email if email else '').first() # Avoid double counting if same person
        
        if by_name:
             matches.append({
                'id': by_name.id,
                'name': f"{by_name.first_name} {by_name.last_name}",
                'email': by_name.email,
                'reason': 'Nombre y Apellido coincidentes'
            })
    
    return JsonResponse({'exists': len(matches) > 0, 'matches': matches})

@login_required
@user_passes_test(is_recruiter)
@login_required
@user_passes_test(is_recruiter)
def dashboard_home(request):
    status_filter = request.GET.get('status', 'active')
    
    # Filter vacancies by status
    if status_filter == 'all':
        vacancies = Vacancy.objects.all()
    else:
        # Default to active if invalid status
        if status_filter not in ['active', 'closed', 'on_hold']:
            status_filter = 'active'
        vacancies = Vacancy.objects.filter(status=status_filter)
    
    # Stats - Total across all statuses
    total_candidates = Candidate.objects.count()
    active_candidates = Candidate.objects.filter(availability_status='active').count()
    recent_applications = Application.objects.order_by('-applied_at')[:5]

    return render(request, 'dashboard/home.html', {
        'vacancies': vacancies,
        'current_filter': status_filter,
        'total_candidates': total_candidates,
        'active_candidates': active_candidates,
        'recent_applications': recent_applications
    })

@login_required
@user_passes_test(is_recruiter)
def close_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    if request.method == 'POST':
        vacancy.status = 'closed'
        vacancy.save()
        messages.success(request, f'La vacante "{vacancy.title}" ha sido cerrada y archivada.')
        return redirect('dashboard_home')
    
    # If GET, confirm page could be shown, but for now we'll rely on JS confirm/POST from kanban
    return redirect('kanban_board', vacancy_id=vacancy.id)

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
    candidates = Candidate.objects.all().order_by('-created_at')
    
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


from utils.gemini_service import extract_candidate_data
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@login_required
@user_passes_test(is_recruiter)
def parse_resume_view(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        
        # Use a safe UUID filename to avoid encoding issues with the AI SDK on Windows
        import uuid
        ext = os.path.splitext(resume_file.name)[1]
        safe_filename = f"{uuid.uuid4()}{ext}"
        
        # Save temporarily to process
        temp_path = default_storage.save(f"tmp/{safe_filename}", ContentFile(resume_file.read()))
        full_temp_path = os.path.join(settings.MEDIA_ROOT, temp_path)
        
        try:
            from utils.document_converter import convert_to_pdf_if_needed
            pdf_path_to_analyze = convert_to_pdf_if_needed(full_temp_path)
            
            data = extract_candidate_data(pdf_path_to_analyze)
            
            # Cleanup temp files
            try:
                if os.path.exists(full_temp_path):
                    os.remove(full_temp_path)
                if pdf_path_to_analyze != full_temp_path and os.path.exists(pdf_path_to_analyze):
                    os.remove(pdf_path_to_analyze)
            except OSError:
                pass
            
            if "error" in data:
                return JsonResponse({'success': False, 'error': data['error']})
                
            return JsonResponse({'success': True, 'data': data})
            
        except Exception as e:
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'No file uploaded'})

@login_required
@user_passes_test(is_recruiter)
def dashboard_settings(request):
    from .models import SystemSettings
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        if api_key:
            settings_obj.gemini_api_key = api_key
            settings_obj.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('dashboard_settings')
            
    return render(request, 'dashboard/settings.html', {'settings': settings_obj})

from dashboard.forms import StaffVacancyForm
from clients.models import Company

@login_required
@user_passes_test(is_recruiter)
def add_vacancy_staff(request):
    if request.method == 'POST':
        form = StaffVacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            company_selector = form.cleaned_data.get('company_selector')
            new_company_name = form.cleaned_data.get('new_company_name')

            if company_selector:
                vacancy.company = company_selector
            elif new_company_name:
                company = Company.objects.create(name=new_company_name)
                vacancy.company = company
                
            vacancy.save()
            messages.success(request, f'La oferta "{vacancy.title}" ha sido publicada correctamente.')
            return redirect('dashboard_home')
    else:
        form = StaffVacancyForm()
        
    return render(request, 'dashboard/add_vacancy.html', {'form': form})
