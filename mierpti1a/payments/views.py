from django.shortcuts import render, redirect, get_list_or_404
from .models import Pago, DetalleTarjeta, DetallePayPal, DetalleVale
from django.http import HttpResponse, HttpResponseBadRequest
from django.core import serializers
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def generarPagos(request):
    return render(request, 'pagos.html')

def api_pagos(request):
    if request.method == 'POST':  # Cambiar a POST para solicitudes con JSON
        try:
            # Cargar el cuerpo JSON de la solicitud
            data = json.loads(request.body)

            # Obtener los parámetros desde el JSON
            cliente_id = data.get('clientId')
            tipo = data.get('paymentType')
            monto = data.get('amount')

            if not all([cliente_id, tipo, monto]):
                return JsonResponse({"error": "Faltan campos requeridos", "status": "failure"}, status=400)

            # Crear el pago
            pago = Pago.objects.create(cliente_id=cliente_id, tipo=tipo, monto=monto)

            if tipo == 'Tarjeta':
                DetalleTarjeta.objects.create(
                    pago=pago,
                    nombre_titular=data.get('cardHolder'),
                    no_tarjeta=data.get('cardNumber'),
                    fecha_vencimiento=data.get('expiryDate'),
                    cvv=data.get('cvv')
                )
            elif tipo == 'Paypal':
                DetallePayPal.objects.create(
                    pago=pago,
                    nombre_titular=data.get('paypalHolder'),
                    email=data.get('paypalEmail')
                )
            elif tipo == 'Vale':
                DetalleVale.objects.create(
                    pago=pago,
                    numero_vale=data.get('voucherNumber')
                )

            return JsonResponse({"message": "Pago creado exitosamente", "status": "success"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido", "status": "failure"}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Falta un campo requerido: {e}", "status": "failure"}, status=400)

    return JsonResponse({"error": "Método no permitido", "status": "failure"}, status=405)



def pagosClientes(request):
    return render(request, 'detallesPagos.html')



def api_pagos_por_cliente(request):
    if request.method == 'POST':  # Cambiar a POST para solicitudes con JSON
        try:
            # Cargar el cuerpo JSON de la solicitud
            data = json.loads(request.body)

            # Obtener el cliente_id desde el JSON
            cliente_id = data.get('cliente_id')

            if not cliente_id:
                return JsonResponse({"error": "El campo 'cliente_id' es requerido", "status": "failure"}, status=400)

            pagos = Pago.objects.filter(cliente_id=cliente_id)

            if not pagos.exists():
                return JsonResponse({"error": f"No se encontraron pagos para el cliente con ID {cliente_id}", "status": "failure"}, status=404)

            # Convertir los pagos a JSON
            pagos_json = serializers.serialize('json', pagos)
            return JsonResponse({"pagos": pagos_json, "status": "success"}, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido", "status": "failure"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e), "status": "failure"}, status=500)

    return JsonResponse({"error": "Método no permitido", "status": "failure"}, status=405)
