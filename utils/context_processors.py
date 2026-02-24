from django.conf import settings

def turnstile_keys(request):
    """
    Context processor to make the Turnstile public site key available in all templates.
    """
    return {
        'TURNSTILE_SITE_KEY': getattr(settings, 'TURNSTILE_SITE_KEY', '')
    }
