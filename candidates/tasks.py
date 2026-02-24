import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from candidates.models import Candidate

logger = logging.getLogger(__name__)

@shared_task
def send_reengagement_emails_task():
    """
    Celery task to send re-engagement emails to candidates inactive for > 6 months.
    """
    logger.info("Starting send_reengagement_emails_task")
    six_months_ago = timezone.now() - timedelta(days=180)
    dormant_candidates = Candidate.objects.filter(last_updated__lt=six_months_ago, availability_status='active')
    
    count = dormant_candidates.count()
    logger.info(f"Found {count} dormant candidates.")

    emails_sent = 0
    for candidate in dormant_candidates:
        token_link = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS[0] != '*' else 'http://127.0.0.1:8000'}/candidates/update/{candidate.update_token}/"
        if not token_link.startswith('http'):
             token_link = 'https://' + token_link
             
        subject = "Are you still looking for a job?"
        message = f"Hello {candidate.first_name},\n\We haven't heard from you in a while! Please confirm if you are still looking for opportunities by visiting this link: {token_link}\n\nBest regards,\nHR Team"
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [candidate.email],
                fail_silently=False,
            )
            logger.info(f"Successfully sent email to: {candidate.email}")
            emails_sent += 1
            
            # Optionally mark candidate as notified or something similar
            
        except Exception as e:
            logger.error(f"Failed to send email to {candidate.email}: {str(e)}")

    logger.info(f"Finished send_reengagement_emails_task. Total sent: {emails_sent}")
    return f"Sent {emails_sent} emails out of {count} dormant profiles."
