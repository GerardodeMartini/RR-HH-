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
from utils.turnstile import validate_turnstile

def candidate_login(request):
    if request.method == 'POST':
        # Turnstile validation
        turnstile_result = validate_turnstile(request)
        if not turnstile_result.get('success'):
            messages.error(request, turnstile_result.get('error', 'Error de verificación de seguridad (Captcha).'))
            return render(request, 'candidates/login.html', {'form': AuthenticationForm()})

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.first_name or user.username}!')
            return redirect('candidate_dashboard')
        else:
            # Check if user exists but is not active yet (email unverified)
            username = request.POST.get('username', '').strip()
            user_obj = User.objects.filter(username__iexact=username).first()
            if not user_obj:
                user_obj = User.objects.filter(email__iexact=username).first()

            if user_obj and not user_obj.is_active:
                messages.error(request, '⚠️ Tu cuenta aún no ha sido activada. Por favor revisa el correo electrónico que te enviamos (incluyendo la carpeta de Spam) y presiona "Activar mi cuenta".')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos. Por favor verifica tus credenciales.')
            return render(request, 'candidates/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'candidates/login.html', {'form': form})

def candidate_register(request):
    if request.method == 'POST':
        # Turnstile validation
        turnstile_result = validate_turnstile(request)
        if not turnstile_result.get('success'):
            messages.error(request, turnstile_result.get('error', 'Error de verificación de seguridad (Captcha).'))
            return render(request, 'candidates/register.html', {'form': CandidateRegisterForm(request.POST)})

        form = CandidateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until email verification
            user.save()
            
            # Link candidate profile to user with real name
            candidate_obj = Candidate.objects.filter(email__iexact=user.email).first()
            if candidate_obj:
                candidate_obj.user = user
                if user.first_name:
                    candidate_obj.first_name = user.first_name
                if user.last_name:
                    candidate_obj.last_name = user.last_name
                candidate_obj.save()
            else:
                candidate_obj = Candidate.objects.create(
                    user=user, 
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            
            from utils.emails import send_activation_email
            send_activation_email(request, user, 'activate_candidate')
            
            messages.info(request, "¡Registro casi completo! Te hemos enviado un correo electrónico con un enlace para verificar tu cuenta. 📌 Recuerda que es necesario activar tu cuenta para poder subir tu currículum y postularte a vacantes, garantizando que todas las notificaciones lleguen correctamente a tu casilla de correo.")
            return redirect('candidate_login')
    else:
        form = CandidateRegisterForm()
    return render(request, 'candidates/register.html', {'form': form})

@login_required
def candidate_dashboard(request):
    # Block staff and company users from accessing the candidate portal
    if request.user.is_staff or hasattr(request.user, 'company_profile'):
        messages.error(request, 'Este portal es exclusivo para candidatos.')
        return redirect('vacancy_list')
        
    # Ensure user has a candidate profile linked
    candidate = Candidate.objects.filter(user=request.user).first()
    if not candidate:
        candidate = Candidate.objects.filter(email__iexact=request.user.email).first()
        if candidate:
            candidate.user = request.user
            candidate.save()
        else:
            candidate = Candidate.objects.create(
                user=request.user,
                email=request.user.email,
                first_name=request.user.first_name or "",
                last_name=request.user.last_name or ""
            )

    if candidate.first_name == request.user.username:
        if request.user.first_name and request.user.first_name != request.user.username:
            candidate.first_name = request.user.first_name
            candidate.last_name = request.user.last_name
            candidate.save()
        else:
            candidate.first_name = ""
            candidate.save()
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate_obj = form.save()
            try:
                from utils.document_converter import ensure_pdf_resume
                ensure_pdf_resume(candidate_obj)
            except ImportError:
                pass
            messages.success(request, '¡Perfil y CV actualizados correctamente!')
            return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Hubo un error al guardar los datos del perfil. Por favor revisa los campos en rojo.')
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
