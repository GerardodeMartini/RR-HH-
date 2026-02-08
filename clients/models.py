from django.db import models

from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company_profile')
    name = models.CharField(max_length=200)
    industry = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    company = models.ForeignKey(Company, related_name='contacts', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company.name})"

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
    ]

    company = models.ForeignKey(Company, related_name='vacancies', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField(blank=True, help_text="Comma-separated skills required for ranking (e.g. Python, Django, SQL)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class KillerQuestion(models.Model):
    vacancy = models.ForeignKey(Vacancy, related_name='killer_questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)
    
    def __str__(self):
        return self.text
