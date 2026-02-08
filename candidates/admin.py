from django.contrib import admin
from django.utils.html import format_html
from .models import Candidate, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'availability_status', 'resume_link', 'last_updated')
    list_filter = ('availability_status', 'tags')
    search_fields = ('first_name', 'last_name', 'email', 'skills')
    filter_horizontal = ('tags',)
    readonly_fields = ('update_token', 'last_updated')

    def changelist_view(self, request, extra_context=None):
        # Database Quality Metrics
        total = Candidate.objects.count()
        active = Candidate.objects.filter(availability_status='active').count()
        dormant = Candidate.objects.filter(availability_status='not_looking').count()
        
        active_pct = int((active / total * 100)) if total > 0 else 0
        
        extra_context = extra_context or {}
        extra_context['quality_metrics'] = {
            'total': total,
            'active_pct': active_pct,
            'dormant': dormant,
        }
        return super().changelist_view(request, extra_context=extra_context)

    def resume_link(self, obj):
        if obj.resume_file:
            return format_html('<a href="{}" target="_blank">Download CV</a>', obj.resume_file.url)
        return "No CV"
    resume_link.short_description = 'Resume'

