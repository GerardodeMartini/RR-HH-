from django.contrib import admin
from .models import Company, Contact, Vacancy, KillerQuestion

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1

class KillerQuestionInline(admin.TabularInline):
    model = KillerQuestion
    extra = 1

class VacancyInline(admin.TabularInline):
    model = Vacancy
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'created_at')
    inlines = [ContactInline, VacancyInline]
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'status')
    list_filter = ('status', 'company')
    search_fields = ('title', 'description', 'required_skills')
    inlines = [KillerQuestionInline]
