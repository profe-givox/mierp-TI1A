# Django imports
from django.shortcuts import render, redirect, get_list_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# Models
from .models import Pago, DetalleTarjeta, DetallePayPal, DetalleVale
from shipments.models import Orden, DetalleOrden, Address
from ecar.models import Carrito, CarritoProducto

# Standard library imports
import json
import requests



from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest



from django.http import HttpResponseForbidden
import json
from urllib.parse import unquote,urlparse

from django.http import JsonResponse
from django.http import JsonResponse

def check_origin_payments(func):
    def wrap(request, *args, **kwargs):
        # Obtener la URL de la página de donde proviene la solicitud
        referer = request.META.get('HTTP_REFERER', 'No disponible')
        print(f"Solicitud proveniente de: {referer}")

        path = urlparse(referer).path
        print(f"Solicitud proveniente de path: {path}")

        allowed_origins = ['/ecar/carrito/']
        if path not in allowed_origins:
            return JsonResponse({'error': 'Acceso no permitido'}, status=403)

        return func(request, *args, **kwargs)

    return wrap

from django.http import JsonResponse

def check_js_request(func):
    def wrap(request, *args, **kwargs):
        # Imprimir el valor del encabezado 'X-Requested-With' para depuración
        print("Encabezado X-Requested-With:", request.headers.get('X-Requested-With'))
        
        # Verificar si el encabezado 'X-Requested-With' está presente y es 'XMLHttpRequest'
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'Acceso solo permitido desde JavaScript'}, status=403)
        
        referer = request.META.get('HTTP_REFERER', 'Desconocido')
        print("Solicitud realizada desde:", referer)

        # Extraer solo la ruta de la URL referer
        path = urlparse(referer).path
        allowed_paths = ['/payments/api_pagos/','/payments/pagos/']  # Rutas permitidas
        if path not in allowed_paths:
            return JsonResponse({'error': 'Origen no permitido'}, status=403)

        return func(request, *args, **kwargs)

    return wrap



@check_origin_payments
@login_required(login_url='/ecar/login/')
def generarPagos(request):
    if request.method == 'POST':
        # Obtener el parámetro 'amount' desde el cuerpo de la solicitud
        amount = request.POST.get('amount')
        if amount is None:
            return HttpResponseBadRequest("El parámetro 'amount' es obligatorio.")
        
        try:
            # Convertir el parámetro a Decimal
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return HttpResponseBadRequest("El parámetro 'amount' debe ser un número válido.")

        # Procesar el pago o pasar el monto al template
        return render(request, 'pagos.html', {'amount': amount})
    
    return render(request, 'pagos.html')  # GET por defecto

@check_js_request
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
            
            if int(cliente_id) != request.user.id:
                return JsonResponse({"error": "El cliente_id no coincide con el usuario autenticado", "status": "failure"}, status=403)

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

            return JsonResponse({
                "message": "Pago creado exitosamente",
                "status": "success",
                "payment_id": pago.id
            })

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


def pagoExitoso(request):
    return render(request, 'succesful.html')

@login_required(login_url='/ecar/login/')
@check_js_request
def generarPedido(request):

    if request.method == 'POST':
        try:
            # Parsear el cuerpo de la solicitud
            data = json.loads(request.body)
            pago_id = data.get('pago_id')
            print(f"pago: {pago_id}")
            if not pago_id:
                return JsonResponse({'error': 'El ID del pago es obligatorio.'}, status=400)
            
            # Obtener el carrito del usuario
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
            productos_carrito = CarritoProducto.objects.filter(carrito=carrito)
            print(f"seguimos")
            # Simulación de API para productos
            try:
                response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
                if response.status_code == 200:
                    productos_data = response.json().get('productos', [])
                    productos_dict = {producto['id']: producto for producto in productos_data}
                else:
                    productos_dict = {}
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Error al obtener los productos: {e}'}, status=500)

            carrito_actualizado = []
            total = Decimal(0)
            print(f"seguimos2")
            for item in productos_carrito:
                producto_api = productos_dict.get(item.producto.id)
                if producto_api:
                    precio_unitario = Decimal(producto_api.get('precio_unitario', 0))
                    descuento = Decimal(producto_api.get('descuento', 0))
                    precio_con_descuento = (precio_unitario * (1 - descuento / 100)).quantize(Decimal('0.01'))
                    total += precio_con_descuento * item.cantidad
                    carrito_actualizado.append({
                        'producto_id': item.producto.id,
                        'nombre': producto_api.get('nombre', 'Producto no disponible'),
                        'cantidad': item.cantidad,
                        'precio_unitario': precio_unitario,
                        'descuento': descuento,
                        'precio_con_descuento': precio_con_descuento,
                    })
            print(f"seguimos3")
            # Crear la dirección de envío
            address = Address.objects.create(
                user=request.user.id,
                street="C. Ejército Nacional 9, Zona Centro, 38980 Uriangato, Gto., México",
                city="Uriangato",
                state="Guanajuato",
                postal_code="38980",
                latitude=20.13859052392204,
                longitude=-101.17201526930087
            )
            print(f"seguimos4, pagoid = {pago_id}")
            # Crear la orden


            try:
                pagoS = Pago.objects.get(id=pago_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'El pago especificado no existe'}, status=400)

            nueva_orden = Orden.objects.create(
                cliente_id=request.user.id,
                total=total,
                address=address,
                pago  = pagoS
            )
            print(f"seguimos5 : {pagoS}")
            # Guardar los detalles de la orden
            for item in carrito_actualizado:
                DetalleOrden.objects.create(
                    orden=nueva_orden,
                    producto_id=item['producto_id'],
                    nombre=item['nombre'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                    descuento=item['descuento'],
                    precio_con_descuento=item['precio_con_descuento']
                )
            print(f"seguimos6")
            productos_carrito.delete()
            # Retornar respuesta JSON
            return JsonResponse({'orden_id': nueva_orden.id, 'total': float(total), 'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Solicitud inválida.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrió un error: {e}'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)