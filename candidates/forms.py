from django import forms
from .models import Candidate

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email', 'phone', 'resume_file', 'skills']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'resume_file': forms.FileInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, SQL, Django...'}),
        }
