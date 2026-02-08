from django.db import models
from clients.models import Vacancy, KillerQuestion
from candidates.models import Candidate

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied (Postulado)'),
        ('initial_interview', 'Initial Interview (Entrevista Inicial)'),
        ('tech_evaluation', 'Tech Evaluation (Evaluación Técnica)'),
        ('shortlist', 'Shortlist (Terna Final)'),
        ('offer', 'Offer (Oferta)'),
        ('hired', 'Hired (Contratado)'),
        ('rejected', 'Rejected (Descartado)'),
    ]

    vacancy = models.ForeignKey(Vacancy, related_name='applications', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name='applications', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    match_score = models.IntegerField(default=0, help_text="Percentage match based on skills (0-100)")
    applied_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # AI Analysis Fields
    ai_summary = models.TextField(blank=True, help_text="AI-generated summary of the candidate")
    ai_match_score = models.IntegerField(null=True, blank=True, help_text="AI-calculated match score (0-100)")
    ai_feedback = models.TextField(blank=True, help_text="Detailed AI feedback on the match")

    def __str__(self):
        return f"{self.candidate} -> {self.vacancy} ({self.status}) - Match: {self.match_score}%"

    def calculate_match_score(self):
        if not self.vacancy.required_skills or not self.candidate.skills:
            return 0
        
        req_skills = [s.strip().lower() for s in self.vacancy.required_skills.split(',') if s.strip()]
        cand_skills = [s.strip().lower() for s in self.candidate.skills.split(',') if s.strip()]
        
        if not req_skills:
            return 0
            
        matches = sum(1 for skill in req_skills if skill in cand_skills)
        return int((matches / len(req_skills)) * 100)

    def save(self, *args, **kwargs):
        # Auto-calculate match score on save
        self.match_score = self.calculate_match_score()
        super().save(*args, **kwargs)

class Answer(models.Model):
    application = models.ForeignKey(Application, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(KillerQuestion, related_name='answers', on_delete=models.CASCADE)
    response = models.TextField() # Keeping it simple text for now
    
    def __str__(self):
        return f"Ans: {self.response} ({self.application})"
