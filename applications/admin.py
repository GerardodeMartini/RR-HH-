from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Application, Answer

def generate_shortlist_pdf(modeladmin, request, queryset):
    template_path = 'pdf/shortlist_pdf.html'
    context = {'applications': queryset}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="terna_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

generate_shortlist_pdf.short_description = "Generate Shortlist PDF (Terna)"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'response')
    can_delete = False

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'vacancy', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'vacancy', 'applied_at')
    search_fields = ('candidate__first_name', 'candidate__last_name', 'vacancy__title')
    readonly_fields = ('match_score',)
    inlines = [AnswerInline]
    actions = [generate_shortlist_pdf]

