from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Candidate

def quick_update_view(request, token):
    candidate = get_object_or_404(Candidate, update_token=token)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            candidate.availability_status = 'active'
        elif action == 'dormant':
            candidate.availability_status = 'not_looking'
        
        # Saving updates last_updated automatically because of auto_now=True
        candidate.save()
        
        return HttpResponse("<h1>Thanks! Your profile has been updated.</h1>")

    return render(request, 'candidates/quick_update.html', {'candidate': candidate})

# --- Candidate Portal Views ---
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from applications.models import Application
from .forms import CandidateProfileForm, CandidateRegisterForm
from utils.emails import send_candidate_welcome

def candidate_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('candidate_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'candidates/login.html', {'form': form})

def candidate_register(request):
    if request.method == 'POST':
        form = CandidateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until email verification
            user.save()
            
            # Link candidate profile to user
            candidate_obj = Candidate.objects.create(
                user=user, 
                email=user.email,
                first_name=user.username
            )
            
            from utils.emails import send_activation_email
            send_activation_email(request, user, 'activate_candidate')
            
            messages.info(request, "¡Registro casi completo! Te hemos enviado un correo electrónico con un enlace para verificar tu cuenta. Por favor, revisa tu bandeja de entrada (y la carpeta de Spam) para activarla y poder iniciar sesión.")
            return redirect('candidate_login')
    else:
        form = CandidateRegisterForm()
    return render(request, 'candidates/register.html', {'form': form})

@login_required
def candidate_dashboard(request):
    # Ensure user has a candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate_obj = form.save()
            try:
                from utils.document_converter import ensure_pdf_resume
                ensure_pdf_resume(candidate_obj)
            except ImportError:
                pass
            return redirect('candidate_dashboard')
    else:
        form = CandidateProfileForm(instance=candidate)
    
    applications = Application.objects.filter(candidate=candidate).order_by('-applied_at')
    
    # Get IDs of vacancies the candidate has already applied for
    applied_vacancy_ids = applications.values_list('vacancy_id', flat=True)
    
    from clients.models import Vacancy
    vacancies = Vacancy.objects.filter(status='active').exclude(id__in=applied_vacancy_ids).order_by('-created_at')
    
    return render(request, 'candidates/dashboard.html', {
        'candidate': candidate,
        'applications': applications,
        'vacancies': vacancies,
        'form': form
    })

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from utils.emails import send_candidate_welcome

def activate_candidate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Enviar correo final de bienvenida si existe el perfil asociado
        if hasattr(user, 'candidate_profile'):
            send_candidate_welcome(user.candidate_profile)
            
        messages.success(request, "¡Cuenta activada exitosamente! Ya puedes iniciar sesión con tus credenciales.")
        return redirect('candidate_login')
    else:
        messages.error(request, "El enlace de activación es inválido o ha caducado. Es posible que tu cuenta ya haya sido activada, intenta iniciar sesión.")
        return redirect('candidate_login')
