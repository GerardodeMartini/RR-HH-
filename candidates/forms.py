from django import forms
from .models import Candidate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from utils.turnstile import TurnstileField

class CandidateProfileForm(forms.ModelForm):
    # Override email to be CharField to accept multiple emails
    email = forms.CharField(
        label='Correo Electrónico',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ej: usuario@mail.com, otro@mail.com'}),
        help_text="Puede ingresar múltiples correos separados por coma."
    )

    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email', 'phone', 'resume_file', 'skills']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'Teléfono',
            'resume_file': 'Currículum (CV)',
            'skills': 'Habilidades / Skills',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, SQL, Django...'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            initial = kwargs.get('initial', {})
            # Combine primary and secondary emails for display
            emails = [instance.email]
            if instance.secondary_email:
                # Split secondary emails by comma and clean whitespace
                secondaries = [e.strip() for e in instance.secondary_email.split(',') if e.strip()]
                emails.extend(secondaries)
            initial['email'] = ', '.join(emails)
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email_input = self.cleaned_data.get('email')
        if not email_input:
            raise forms.ValidationError("Este campo es obligatorio.")
        
        # Split by comma
        emails = [e.strip() for e in email_input.split(',') if e.strip()]
        
        # Validate each email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        for e in emails:
            try:
                validate_email(e)
            except ValidationError:
                raise forms.ValidationError(f"'{e}' no es una dirección de correo válida.")
        
        # Check uniqueness of the PRIMARY email (the first one)
        primary_email = emails[0]
        
        # Exclude self if updating
        qs = Candidate.objects.filter(email__iexact=primary_email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise forms.ValidationError(f"El correo principal '{primary_email}' ya está registrado.")
            
        return email_input

    def save(self, commit=True):
        candidate = super().save(commit=False)
        
        # Split email input
        email_input = self.cleaned_data.get('email')
        emails = [e.strip() for e in email_input.split(',') if e.strip()]
        
        if emails:
            candidate.email = emails[0] # Primary
            candidate.secondary_email = ', '.join(emails[1:]) # Rest
        
        if commit:
            candidate.save()
            self.save_m2m()
            
        return candidate

class CandidateRegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}))
    last_name = forms.CharField(label='Apellido', max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}))
    turnstile = TurnstileField()

    username = forms.CharField(label='Usuario', max_length=20, help_text='Requerido. 20 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ej: juanperez'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Usuario',
            'email': 'Correo Electrónico',
        }
        help_texts = {
            'username': 'Requerido. 20 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'email': 'Dirección de correo válida.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Candidate.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo electrónico ya se encuentra registrado en RRHH MARINA. Por favor, utiliza otro o recupera tu contraseña.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = "Usuario"
        self.fields['email'].label = "Correo Electrónico" 
        self.fields['email'].required = True
        
        # Check if fields exist before accessing (UserCreationForm standard fields)
        if 'password1' in self.fields:
            self.fields['password1'].label = "Contraseña"
            self.fields['password1'].help_text = "La contraseña debe tener al menos 8 caracteres y no ser demasiado común."
            self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        
        if 'password2' in self.fields:
            self.fields['password2'].label = "Confirmar contraseña"
            self.fields['password2'].help_text = "Ingresa la misma contraseña para verificar."
            self.fields['password2'].widget.attrs.update({'class': 'form-control'})
