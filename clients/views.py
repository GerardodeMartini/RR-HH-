from django.shortcuts import render, get_object_or_404, redirect
from .models import Vacancy, Company
from candidates.models import Candidate
from applications.models import Application, Answer

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='active').order_by('-created_at')
    return render(request, 'vacancy_list.html', {'vacancies': vacancies})

def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
    if request.method == 'POST':
        # 1. Create/Update Candidate
        email = request.POST.get('email')
        candidate, created = Candidate.objects.get_or_create(email=email)
        
        candidate.first_name = request.POST.get('first_name')
        candidate.last_name = request.POST.get('last_name')
        candidate.phone = request.POST.get('phone')
        candidate.skills = request.POST.get('skills')
        
        if 'resume' in request.FILES:
            candidate.resume_file = request.FILES['resume']
        
        candidate.save()
        
        # 2. Create Application
        application, app_created = Application.objects.get_or_create(
            vacancy=vacancy,
            candidate=candidate
        )
        
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

    return render(request, 'vacancy_detail.html', {
        'vacancy': vacancy,
        'killer_questions': vacancy.killer_questions.filter(is_required=True)
    })
