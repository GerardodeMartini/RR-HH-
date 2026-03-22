from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Vacancy, Company
from .forms import VacancyForm, CompanyProfileForm, CompanyRegisterForm
from applications.models import Application
from candidates.models import Candidate

from utils.turnstile import validate_turnstile
from django.contrib import messages
from utils.emails import (
    send_company_welcome,
    send_company_vacancy_confirmation,
    send_staff_new_vacancy
)

class CompanyLoginView(LoginView):
    template_name = 'clients/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/empresas/'

    def post(self, request, *args, **kwargs):
        turnstile_result = validate_turnstile(request)
        if not turnstile_result.get('success'):
            messages.error(request, 'Error de verificación de seguridad (Captcha). Por favor, intenta de nuevo.')
            return render(request, self.template_name, {'form': self.get_form()})
            
        return super().post(request, *args, **kwargs)

def company_register(request):
    if request.method == 'POST':
        form = CompanyRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False # Deactivate until email verification
            user.save()
            
            from utils.emails import send_activation_email
            send_activation_email(request, user, 'activate_company')
            
            messages.info(request, "¡Registro casi completo! Te hemos enviado un correo electrónico con un enlace para verificar tu cuenta de empresa. Por favor, revisa tu bandeja de entrada (y la carpeta de Spam) para activarla y poder iniciar sesión.")
            return redirect('client_login')
    else:
        form = CompanyRegisterForm()
    return render(request, 'clients/register.html', {'form': form})

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

def activate_company(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        if hasattr(user, 'company_profile'):
            from utils.emails import send_company_welcome
            send_company_welcome(user.company_profile)
            
        messages.success(request, "¡Cuenta de empresa activada exitosamente! Ya puedes iniciar sesión.")
        return redirect('client_login')
    else:
        messages.error(request, "El enlace de activación es inválido o ha caducado. Es posible que tu cuenta ya haya sido activada.")
        return redirect('client_login')

def check_company_profile(user):
    return hasattr(user, 'company_profile')

@login_required(login_url='client_login')
def client_portal_home(request):
    # Check if user has a company profile
    if not hasattr(request.user, 'company_profile'):
        return render(request, 'clients/no_profile.html')
    
    company = request.user.company_profile
    vacancies = Vacancy.objects.filter(company=company).order_by('-created_at')
    
    return render(request, 'clients/portal_home.html', {
        'company': company,
        'vacancies': vacancies
    })

@login_required(login_url='client_login')
def client_vacancy_view(request, vacancy_id):
    if not hasattr(request.user, 'company_profile'):
        return render(request, 'clients/no_profile.html')
        
    company = request.user.company_profile
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, company=company)
    
    # Show Candidates
    # 1. New Applicants (Applied, Interviewing)
    new_applicants = Application.objects.filter(
        vacancy=vacancy,
        status__in=['applied', 'initial_interview', 'tech_evaluation']
    ).order_by('-match_score')

    # 2. Finalists (The "Terna")
    shortlisted_apps = Application.objects.filter(
        vacancy=vacancy,
        status__in=['shortlist', 'offer', 'hired']
    ).order_by('-match_score')
    
    return render(request, 'clients/portal_vacancy.html', {
        'vacancy': vacancy,
        'new_applicants': new_applicants,
        'shortlisted_apps': shortlisted_apps
    })

@login_required(login_url='client_login')
def create_vacancy(request):
    if not hasattr(request.user, 'company_profile'):
        return render(request, 'clients/no_profile.html')
    
    company = request.user.company_profile
    
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.company = company
            vacancy.save()
            
            # Send email confirmation & staff alert
            send_company_vacancy_confirmation(company, vacancy)
            send_staff_new_vacancy(vacancy)
            
            return redirect('client_portal')
    else:
        form = VacancyForm()
    
    return render(request, 'clients/vacancy_form.html', {'form': form})

@login_required(login_url='client_login')
def company_profile(request):
    if not hasattr(request.user, 'company_profile'):
        return render(request, 'clients/no_profile.html')
    
    company = request.user.company_profile
    
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('client_portal') # Or back to profile
    else:
        form = CompanyProfileForm(instance=company)
    
    return render(request, 'clients/company_profile.html', {'form': form})

@login_required(login_url='client_login')
def talent_pool(request):
    if not hasattr(request.user, 'company_profile'):
        return render(request, 'clients/no_profile.html')
    
    # Show active candidates
    candidates = Candidate.objects.filter(availability_status='active').order_by('-last_updated')
    
    return render(request, 'clients/talent_pool.html', {
        'candidates': candidates
    })
