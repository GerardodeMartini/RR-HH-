class RoleSessionTimeoutMiddleware:
    """
    Middleware que ajusta dinámicamente la expiración de la sesión según el rol:
    - Staff / Reclutadores: 10 minutos (600 segundos) - Cumpliendo normas OWASP para datos sensibles.
    - Candidatos / Empresas: 20 minutos (1200 segundos) - Para permitir lectura y llenado de formularios.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_staff:
                request.session.set_expiry(600)  # 10 minutos
            else:
                request.session.set_expiry(1200) # 20 minutos

        response = self.get_response(request)
        return response
