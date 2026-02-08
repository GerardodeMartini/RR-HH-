from django.db import models
import uuid

from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    AVAILABILITY_CHOICES = [
        ('active', 'Active (Looking)'),
        ('open', 'Open to Offers (Listening)'),
        ('not_looking', 'Not Looking (Dormant)'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='candidate_profile')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills or description")
    tags = models.ManyToManyField(Tag, blank=True, related_name='candidates')
    
    # Automation Fields
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='active')
    last_updated = models.DateTimeField(auto_now=True)
    update_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
