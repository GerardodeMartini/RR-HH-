from django import forms
from .models import Vacancy, KillerQuestion, Company

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'required_skills']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Desarrollador Python Senior'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe el puesto, responsabilidades y beneficios...'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, SQL, Inglés (Separados por coma)'}),
        }
        labels = {
            'title': 'Título del Puesto',
            'description': 'Descripción',
            'required_skills': 'Habilidades Requeridas',
        }

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'industry', 'description', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Tecnología, Salud, Finanzas'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre de la Empresa',
            'industry': 'Rubro / Industria',
            'description': 'Descripción',
            'email': 'Email de Contacto',
            'phone': 'Teléfono',
        }
