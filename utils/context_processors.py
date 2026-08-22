from django.conf import settings

def turnstile_keys(request):
    """
    Context processor to make the Turnstile public site key available in all templates.
    """
    return {
        'TURNSTILE_SITE_KEY': getattr(settings, 'TURNSTILE_SITE_KEY', '')
    }

def session_timeout_info(request):
    """
    Context processor to provide session timeout duration to JavaScript in templates.
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.is_staff:
            timeout_seconds = 600  # 10 minutos
            timeout_minutes = 10
        else:
            timeout_seconds = 1200 # 20 minutos
            timeout_minutes = 20
        return {
            'SESSION_TIMEOUT_SECONDS': timeout_seconds,
            'SESSION_TIMEOUT_MINUTES': timeout_minutes,
        }
    return {
        'SESSION_TIMEOUT_SECONDS': 0,
        'SESSION_TIMEOUT_MINUTES': 0,
    }

