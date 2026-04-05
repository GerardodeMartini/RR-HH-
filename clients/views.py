from django.shortcuts import render, get_object_or_404, redirect
from .models import Vacancy, Company
from candidates.models import Candidate
from applications.models import Application, Answer
from utils.emails import send_candidate_application, send_staff_new_application
from django.contrib import messages

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='active').order_by('-created_at')
    return render(request, 'vacancy_list.html', {'vacancies': vacancies})

def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
    # Check if the user is staff early on
    is_staff = request.user.is_authenticated and request.user.is_staff

    if request.method == 'POST':
        # Block staff from applying
        if is_staff:
            # Maybe add a message here in the future if needed
            return redirect('home')

        # 1. Check existing Candidate
        email = request.POST.get('email')
        candidate = Candidate.objects.filter(email=email).first()
        
        if candidate:
            # Candidate exists. If the user is NOT logged in as this candidate, block it to prevent data overwrite.
            user_is_owner = request.user.is_authenticated and getattr(request.user, 'candidate_profile', None) == candidate
            if not user_is_owner:
                messages.error(request, 'Este correo ya está registrado en la plataforma. Por favor, inicia sesión para postularte.')
                return redirect('vacancy_detail', vacancy_id=vacancy.id)
        else:
            candidate = Candidate.objects.create(email=email)
        
        candidate.first_name = request.POST.get('first_name')
        candidate.last_name = request.POST.get('last_name')
        candidate.phone = request.POST.get('phone')
        candidate.skills = request.POST.get('skills')
        
        if 'resume' in request.FILES:
            candidate.resume_file = request.FILES['resume']
        
        candidate.save()
        
        try:
            from utils.document_converter import ensure_pdf_resume
            ensure_pdf_resume(candidate)
        except ImportError:
            pass # Si el módulo falla, la postulación igual avanza
        
        # 2. Create Application
        application, app_created = Application.objects.get_or_create(
            vacancy=vacancy,
            candidate=candidate
        )
        
        if app_created:
            send_candidate_application(candidate, vacancy)
            send_staff_new_application(application)
        
        # 3. Save Killer Question Answers
        for key, value in request.POST.items():
            if key.startswith('question_'):
                q_id = key.split('_')[1]
                question = vacancy.killer_questions.get(id=q_id)
                Answer.objects.create(
                    application=application,
                    question=question,
                    response=value
                )
                
        return render(request, 'application_success.html', {'vacancy': vacancy})

    candidate_profile = None
    is_company = False
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'candidate_profile'):
            candidate_profile = request.user.candidate_profile
        if hasattr(request.user, 'company_profile'):
            is_company = True

    return render(request, 'vacancy_detail.html', {
        'vacancy': vacancy,
        'killer_questions': vacancy.killer_questions.filter(is_required=True),
        'candidate': candidate_profile,
        'is_company': is_company,
        'is_staff': is_staff,
    })
