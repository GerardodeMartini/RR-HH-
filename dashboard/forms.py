from django import forms
from clients.models import Vacancy, Company

class StaffVacancyForm(forms.ModelForm):
    company_selector = forms.ModelChoiceField(
        queryset=Company.objects.all().order_by('name'),
        required=False,
        label="Seleccionar Empresa Registrada",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_company_name = forms.CharField(
        required=False,
        label="O Crear Nueva Empresa Rápida",
        help_text="Escribe el nombre aquí si la empresa no está en la lista.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Librería San Martín'})
    )

    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'required_skills']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cajero Administrativo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe el puesto, responsabilidades y beneficios...'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Excel, Atención al Público (Separados por coma)'}),
        }
        labels = {
            'title': 'Título del Puesto',
            'description': 'Descripción',
            'required_skills': 'Habilidades Requeridas',
        }

    def clean(self):
        cleaned_data = super().clean()
        company_selector = cleaned_data.get('company_selector')
        new_company_name = cleaned_data.get('new_company_name')

        if not company_selector and not new_company_name:
            raise forms.ValidationError("Debes seleccionar una empresa o ingresar el nombre para crear una nueva.")
        
        return cleaned_data
