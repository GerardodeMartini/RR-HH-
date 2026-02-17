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
from applications.models import Application
from .forms import CandidateProfileForm, CandidateRegisterForm

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
            user = form.save()
            # Link candidate profile to user
            Candidate.objects.create(
                user=user, 
                email=user.email,
                first_name=user.username
            )
            login(request, user)
            return redirect('candidate_dashboard')
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
            form.save()
            return redirect('candidate_dashboard')
    else:
        form = CandidateProfileForm(instance=candidate)
    
    applications = Application.objects.filter(candidate=candidate).order_by('-applied_at')
    
    return render(request, 'candidates/dashboard.html', {
        'candidate': candidate,
        'applications': applications,
        'form': form
    })

