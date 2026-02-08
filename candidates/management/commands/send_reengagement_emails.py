from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from candidates.models import Candidate

class Command(BaseCommand):
    help = 'Send re-engagement emails to candidates inactive for > 6 months'

    def handle(self, *args, **options):
        six_months_ago = timezone.now() - timedelta(days=180)
        dormant_candidates = Candidate.objects.filter(last_updated__lt=six_months_ago, availability_status='active')
        
        count = dormant_candidates.count()
        self.stdout.write(f"Found {count} dormant candidates.")

        for candidate in dormant_candidates:
            # In a real scenario, use django.core.mail.send_mail
            token_link = f"http://127.0.0.1:8000/candidates/update/{candidate.update_token}/"
            
            # Simulating Email Sending
            self.stdout.write(self.style.SUCCESS(f"Sending email to: {candidate.email}"))
            self.stdout.write(f"Subject: Are you still looking?")
            self.stdout.write(f"Body: Hello {candidate.first_name}, please confirm your status: {token_link}\n")
            
            # Mark as 'notified' or similar logic could go here to avoid spamming.
            # For this demo, we just log it.
