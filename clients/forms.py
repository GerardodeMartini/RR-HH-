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

from django.contrib.auth.models import User
from utils.turnstile import TurnstileField

class CompanyRegisterForm(forms.ModelForm):
    # User fields
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Company fields
    company_name = forms.CharField(label="Nombre de la Empresa", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email de Contacto", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Teléfono", widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    turnstile = TurnstileField()

    class Meta:
        model = Company
        fields = ['company_name', 'industry', 'email', 'phone'] # Industry is in model but not here? Let's add it.
        # Actually, let's include industry in the form fields above or in Meta.
        # Let's keep it simple: Username, Pwd, Name, Email, Phone. Industry can be updated later or added.
        # Let's add industry to be safe.
    
    industry = forms.CharField(label="Industria", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
            
        username = cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
             self.add_error('username', "Este nombre de usuario ya está en uso.")
             
        email = cleaned_data.get("email")
        if email and (User.objects.filter(email__iexact=email).exists() or Company.objects.filter(email__iexact=email).exists()):
             self.add_error('email', "Este correo electrónico ya se encuentra registrado en RRHH MARINA. Por favor, utiliza otro o recupera tu contraseña.")
             
        return cleaned_data

    def save(self, commit=True):
        # 1. Create User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'] 
            # Note: email in User model vs Company model. We save to both for convenience.
        )
        
        # 2. Create Company
        company = Company.objects.create(
            user=user,
            name=self.cleaned_data['company_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            industry=self.cleaned_data.get('industry', '')
        )
        
        return user
