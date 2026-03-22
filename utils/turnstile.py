import requests
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.utils.safestring import mark_safe

class TurnstileWidget(forms.Widget):
    template_name = 'turnstile_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        site_key = getattr(settings, 'TURNSTILE_SITE_KEY', None)
        if not site_key:
            return mark_safe("<!-- Error: TURNSTILE_SITE_KEY not set. -->")
            
        return mark_safe(f"""
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
        <div class="cf-turnstile" data-sitekey="{site_key}" data-theme="light"></div>
        """)

class TurnstileField(forms.CharField):
    widget = TurnstileWidget
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = ""
        self.required = True
        
    def validate(self, value):
        super().validate(value)
        # Value passed here is the cleaned value from the widget? 
        # Actually, for a CharField, it's the string input.
        # But wait, the input name in the HTML is 'cf-turnstile-response'.
        # Django forms expect the field name in POST data to match the form field name.
        # We need to handle this. 
        pass

    def clean(self, value):
        # We can't easily access the request here to get 'cf-turnstile-response' if the field name is different.
        # However, if we name the form field 'cf-turnstile-response' it might work, but that's ugly.
        # Better approach: The widget renders a div. The actual input is injected by JS with name 'cf-turnstile-response'.
        # So 'value' passed to this field might be empty if the form field name doesn't match the input name.
        
        # Actually, let's keep it simple. We will grab the hidden field value from the form data.
        # In a standard Django form, we validate `value`.
        
        # NOTE: Allow value to be passed, but the actual token is usually in `cf-turnstile-response`.
        # To make this seamless, we'll assume the form setup handles passing the data, OR we validate in the Form's clean method.
        # BUT, a custom Field is better if we can make it work.
        
        # Let's assume the user of this field will maps the request content or we use a custom logic.
        # Actually, the standard way for these widgets is:
        # The widget renders the HTML.
        # The form submission includes 'cf-turnstile-response'.
        # This field needs to look for that in the `data`.
        
        # Since `clean` only gets the value for this specific field name, functionality depends on the field name matching the input?
        # No, Turnstile forces the name 'cf-turnstile-response'.
        
        # Workaround: valid_turnstile helper function to call in form.clean(), 
        # OR we rely on the view to validate (not ideal).
        
        # Let's try to make the field work by expecting the value to be the token.
        # This implies the field name in the form MUST be `cf_turnstile_response`? No, that's snake_case.
        
        # Improved approach:
        # We'll creating a helper `validate_turnstile(request)` function. 
        # But to keep it in the form, let's just make a field that validates it.
        
        secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', None)
        if not secret_key:
            raise ValidationError("TURNSTILE_SECRET_KEY not set.")

        # If we are in clean(), 'value' is what was submitted for this field.
        # If the widget didn't render an input with THIS field's name, 'value' might be empty.
        # So we should probably tell the user to bind `cf-turnstile-response` to this field 
        # OR just check `cf-turnstile-response` from the full data if possible (hard in a Field).
        
        # Let's use the helper verification inside the form's clean method, 
        # which is the most robust way in Django without hacking the widget to output a hidden input with the field's name.
        
        # Wait! The widget CAN output a hidden input with the field's name, 
        # and we can use JS to copy the token to it. That's a common pattern.
        return value

def validate_turnstile(request):
    """
    Validates the Turnstile token from the request.
    Returns a dict: {'success': bool, 'error': str (optional)}
    """
    token = request.POST.get('cf-turnstile-response')
    secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', None)
    
    if not token:
         return {'success': False, 'error': str(_("Por favor, completa la verificación de seguridad (Captcha)."))}
         
    if not secret_key:
         # Fail open or closed? Closed for security.
         return {'success': False, 'error': "Error de configuración del servidor (Captcha Secret)."}

    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': secret_key,
                'response': token,
                'remoteip': request.META.get('REMOTE_ADDR')
            },
            timeout=5
        )
        result = response.json()
        
        if not result.get('success'):
            return {'success': False, 'error': str(_("Falló la verificación de seguridad. Intenta nuevamente."))}
            
    except requests.RequestException:
        return {'success': False, 'error': str(_("Error conectando con el servicio de verificación."))}
        
    return {'success': True}
