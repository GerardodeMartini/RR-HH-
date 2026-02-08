from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Vacancy, Company
from .forms import VacancyForm, CompanyProfileForm
from applications.models import Application
from candidates.models import Candidate

class CompanyLoginView(LoginView):
    template_name = 'clients/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/portal/'

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
