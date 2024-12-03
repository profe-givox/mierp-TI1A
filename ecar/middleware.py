from django.http import JsonResponse

class CheckOriginAPIMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/ecar/api/'):
            referer = request.META.get('HTTP_REFERER', 'No disponible')
            allowed_origins = [
                'http://127.0.0.1:8000/ecar/catalogo/',
                'http://127.0.0.1:8000/ecar/carrito/',
                'http://127.0.0.1:8000/pos/api_productos/'
            ]
            if referer not in allowed_origins:
                return JsonResponse({'error': 'Acceso no permitido'}, status=403)
        return self.get_response(request)

    # def __call__(self, request):
    #     # Comprueba si la solicitud es hacia /ecar/api/
    #     if request.path.startswith('/ecar/api/'):
    #         # Simplemente pasa la solicitud sin restricciones
    #         pass
    #     return self.get_response(request)
