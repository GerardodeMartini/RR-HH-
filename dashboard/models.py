from django.db import models

# Create your models here.
class SystemSettings(models.Model):
    gemini_api_key = models.CharField(max_length=255, blank=True, help_text="API Key for Google Gemini AI")
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SystemSettings.objects.exists():
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return "System Settings"

