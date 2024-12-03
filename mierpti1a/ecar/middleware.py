from django.http import JsonResponse
from urllib.parse import unquote, urlparse
import re

class CheckOriginAPIMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/ecar/api/'):
            referer = request.META.get('HTTP_REFERER', 'No disponible')
            path = urlparse(referer).path
            print(f"Solicitud proveniente de path: {path}")
            allowed_origins = [
                '/ecar/catalogo/',
                '/ecar/carrito/',
                '/pos/api_productos/',
            ]

            if path.startswith('/ecar/producto/') and re.match(r'^/ecar/producto/\d+/$', path):
                return self.get_response(request)

            if path not in allowed_origins:
                return JsonResponse({'error': 'Acceso no permitido'}, status=403)
        
        return self.get_response(request)


    # def __call__(self, request):
    #     # Comprueba si la solicitud es hacia /ecar/api/
    #     if request.path.startswith('/ecar/api/'):
    #         # Simplemente pasa la solicitud sin restricciones
    #         pass
    #     return self.get_response(request)
