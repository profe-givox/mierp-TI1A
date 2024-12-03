from unittest import loader
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Empleado, Salida_Entrada
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
import json 


def horario(request):
    return render(request, 'RRHH/horario.html')

def registro_entrada_salida(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            folio = data.get('folio')
            action = data.get('action')
            password = data.get('password')

            if not folio or not action or not password:
                return JsonResponse({'success': False, 'error': 'Faltan campos requeridos'}, status=400)

            # Autenticación del usuario
            user = authenticate(username=folio, password=password)
            if user is None:
                return JsonResponse({'success': False, 'error': 'Credenciales incorrectas'}, status=400)

            # Obtener el empleado relacionado con el usuario autenticado
            try:
                empleado = Empleado.objects.get(Username=user)
            except Empleado.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=400)

            # Registro de entrada o salida
            nuevo_registro = Salida_Entrada(codigo_empleado=empleado, hora=timezone.now(), opcion=action)
            nuevo_registro.save()

            return JsonResponse({
                'success': True,
                'empleado': {
                    'nombre': empleado.nombre,
                    'foto': empleado.foto.url if empleado.foto else None
                },
                'action': action
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error en el cuerpo de la solicitud'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        folio = data.get('folio')
        password = data.get('password')

        if not folio or not password:
            return Response({'success': False, 'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        # Autenticación del usuario
        user = authenticate(username=folio, password=password)
        if user is None:
            return Response({'success': False, 'error': 'Credenciales incorrectas'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el empleado relacionado con el usuario autenticado
        try:
            empleado = Empleado.objects.get(Username=user)
        except Empleado.DoesNotExist:
            return Response({'success': False, 'error': 'Empleado no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        print(empleado.sucursal_id)

        return Response({
            'success': True,
            'empleado': {
                'id': str(empleado.id),
                'nombre': str(empleado.nombre),
                'apellidos': str(empleado.apellidos),
                'sucursal': str(empleado.sucursal_id),
                'nombre_sucursal': str(empleado.sucursal),
                'puesto': str(empleado.puesto),
            },
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        return Response({'success': False, 'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
def get_sucursales(request):
    sucursales = list(Sucursal.objects.values())

    if len(sucursales) > 0:
        data = {'message': "Success", 'sucursales': sucursales}
    else:
        data = {'message': "Not Found"}
    
    return JsonResponse(data)

def get_empleados(request):
    empleados = list(Empleado.objects.values())

    if len(empleados) > 0:
        data= {'message': "Success", 'empleados':empleados}
    else:
        data = {'message': "Not found"}
    return JsonResponse(data)

