import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Constante para forzar que llegue a Marina
MODO_PRUEBA_BCC = 'zubianiasociados@gmail.com'

def get_base_html(title, message, button_text=None, button_url=None):
    """
    Genera el HTML base estilizado estilo 'Zubiani Asociados'
    """
    button_html = ""
    if button_text and button_url:
        button_html = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center">
                    <a href="{button_url}" style="background-color: #D6A87C; color: #FFFFFF; display: inline-block; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; letter-spacing: 0.5px;">{button_text}</a>
                </td>
            </tr>
        </table>
        """

    return f"""\
    <!DOCTYPE html>
    <html>
    <body style="margin: 0; padding: 0; background-color: #F8F7F3; font-family: 'Helvetica Neue', Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F8F7F3; padding: 40px 10px;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #FFFFFF; border-radius: 12px; max-width: 550px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); overflow: hidden;">
                        <tr>
                            <td style="background-color: #4A5D50; padding: 30px 40px; text-align: center;">
                                <h1 style="color: #FFFFFF; margin: 0; font-size: 24px; font-weight: 300; letter-spacing: 2px;">ZUBIANI ASOCIADOS</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="color: #333333; margin-top: 0; font-size: 20px; font-weight: 500;">{title}</h2>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                                    {message}
                                </p>
                                {button_html}
                                <p style="color: #999999; font-size: 14px; line-height: 1.6; margin-top: 40px; margin-bottom: 0; text-align: center;">
                                    Saludos cordiales,<br>El equipo de RRHH MARINA y Zubiani Asociados.
                                </p>
                            </td>
                        </tr>
                    </table>
                    <p style="color: #BBBBBB; font-size: 12px; margin-top: 20px; text-align: center;">Zubiani Asociados &copy; 2026. Todos los derechos reservados.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_stylized_email(subject, to_email, html_content):
    """
    Función core de envío con CC a Gerardo siempre.
    """
    text_content = "ZUBIANI ASOCIADOS - Este correo requiere formato HTML."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'zubianiasociados@zubianirrhh.com.ar')
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email],
        bcc=[MODO_PRUEBA_BCC]  # VERIFICACIÓN
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

# ----- VERIFICACION Y TOKENS -----
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

def send_activation_email(request, user, namespace_activate):
    """
    namespace_activate: e.g. 'activate_candidate' or 'activate_company'
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    relative_link = reverse(namespace_activate, kwargs={'uidb64': uid, 'token': token})
    activation_link = request.build_absolute_uri(relative_link)
    
    subject = "Confirma tu cuenta en RRHH MARINA"
    title = f"¡Hola {user.username}!"
    message = "Para garantizar la seguridad de nuestra plataforma y activar tu perfil, necesitamos que confirmes tu dirección de correo electrónico haciendo clic en el botón de abajo."
    
    html = get_base_html(title, message, "Activar mi Cuenta", activation_link)
    send_stylized_email(subject, user.email, html)

# ----- CANDIDATOS -----
def send_candidate_welcome(candidate):
    subject = "¡Bienvenido a RRHH MARINA!"
    title = f"¡Hola {candidate.first_name}!"
    message = "Tu perfil ha sido creado exitosamente en nuestro portal. Ya puedes comenzar a postularte a las oportunidades laborales disponibles."
    html = get_base_html(title, message, "Ver Vacantes", "https://zubianirrhh.com.ar/")
    send_stylized_email(subject, candidate.email, html)

def send_candidate_application(candidate, vacancy):
    subject = "Postulación Recibida Exitosamente"
    title = f"¡Hola {candidate.first_name}!"
    message = f"Hemos recibido correctamente tu postulación para el puesto de <strong>{vacancy.title}</strong>. Nuestro equipo de selección estará evaluando tu perfil."
    html = get_base_html(title, message)
    send_stylized_email(subject, candidate.email, html)

# ----- EMPRESAS -----
def send_company_welcome(company):
    subject = "¡Bienvenido al Portal de Empresas Zubiani!"
    title = f"¡Hola {company.name}!"
    message = "Tu cuenta de empresa ha sido registrada. Ahora podrás solicitar búsquedas laborales y gestionar candidatos a través de nuestra plataforma."
    html = get_base_html(title, message, "Ir al Portal Empresa", "https://zubianirrhh.com.ar/clients/")
    send_stylized_email(subject, company.email, html)

def send_company_vacancy_confirmation(company, vacancy):
    subject = "Nueva Búsqueda Laboral Registrada"
    title = f"Búsqueda: {vacancy.title}"
    message = f"Hemos registrado tu solicitud para la búsqueda de <strong>{vacancy.title}</strong>. Uno de nuestros selectores se pondrá en marcha a la brevedad."
    html = get_base_html(title, message)
    send_stylized_email(subject, company.email, html)

# ----- STAFF / ADMINISTRADORES -----
def send_staff_new_application(application):
    subject = "[ALERTA] Nueva Postulación Recibida"
    title = "Nueva Postulación"
    candidate = application.candidate
    vacancy = application.vacancy
    message = f"El candidato <strong>{candidate.first_name} {candidate.last_name}</strong> se ha postulado a la vacante <strong>{vacancy.title}</strong>.<br><br>Ver el perfil en el dashboard."
    html = get_base_html(title, message, "Ver Postulación", f"https://zubianirrhh.com.ar/staff/application/{application.id}/")
    send_stylized_email(subject, "zubianiasociados@zubianirrhh.com.ar", html)

def send_staff_new_vacancy(vacancy):
    subject = "[ALERTA] Nueva Solicitud de Vacante"
    title = "Nueva Solicitud de Búsqueda"
    company_name = vacancy.company.name if vacancy.company else "Empresa"
    message = f"La empresa <strong>{company_name}</strong> ha cargado una nueva búsqueda: <strong>{vacancy.title}</strong>.<br><br>Por favor, revisarla en los paneles de administración."
    html = get_base_html(title, message, "Ir al Dashboard", "https://zubianirrhh.com.ar/staff/")
    send_stylized_email(subject, "zubianiasociados@zubianirrhh.com.ar", html)
