from django.core.mail import send_mail
from django.conf import settings

def run():
    print("Iniciando prueba de envío de correo electrónico...")
    try:
        sender = settings.DEFAULT_FROM_EMAIL
        recipient = settings.DEFAULT_FROM_EMAIL  # Enviamos a nosotros mismos (al verificado) para cumplir con el Sandbox
        
        print(f"Enviando desde: {sender}")
        print(f"Hacia (Test): {recipient}")
        
        send_mail(
            subject='Prueba de Amazon SES - RRHH Marina',
            message='¡Hola! Este es un correo de prueba enviado desde tu proyecto Django para verificar la conexión con AWS SES mediante SMTP.',
            from_email=sender,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("\n✅ ¡ÉXITO! El correo fue enviado y aceptado por Amazon SES.")
        print("Revisa tu bandeja de entrada (y la de SPAM) de tu correo verificado.")
    except Exception as e:
        print("\n❌ FALLÓ EL ENVÍO DEL CORREO.")
        print(f"Error devuelto por AWS SES: {str(e)}")
        print("\nPosibles causas:")
        print("1. Las credenciales en el .env (SMTP Username y Password) no son correctas.")
        print("2. El correo en DEFAULT_FROM_EMAIL no está verificado en AWS SES.")
        print("3. Olvidaste guardar los cambios en el archivo .env.")

if __name__ == '__main__':
    run()
