import random
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import models
from .models import Pedido, StockEnPedido, MovimientoInventario
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def ver_productos(request):
    return render(request, 'inventory/ver_productos.html')


def control_inventarios(request):
    return render(request, 'inventory/control_inventarios.html')

def gestion_pedidos(request):
    return render(request, 'inventory/gestion_pedidos.html')

def control_entradas_salidas(request):
    return render(request, 'inventory/control_entradas_salidas.html')

def informes_analisis(request):
    return render(request, 'inventory/informes_analisis.html')

def redirigir_a_productos(request):
    """
    Redirige de /inventory/ a /inventory/productos/.
    """
    return redirect('ver_productos')  # Usa el nombre de la URL para mayor flexibilidad

@csrf_exempt
@login_required
def agregar_pedido(request):
    """
    Vista para agregar un pedido.
    """
    if request.method == 'POST':
        try:
            # Log para depuración
            print("Datos recibidos en el POST:", request.body)

            # Parsear los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad')

            # Validación de datos
            if not producto_id or not cantidad or cantidad <= 0:
                return JsonResponse({'error': 'Producto ID y cantidad válidos son requeridos.'}, status=400)

            # Crear el pedido
            nuevo_pedido = Pedido.objects.create(
                producto_id=producto_id,
                cantidad=cantidad,
                estado='pendiente'
            )

            # Actualizar o crear el registro de StockEnPedido
            stock_pedido, created = StockEnPedido.objects.get_or_create(producto_id=producto_id)
            stock_pedido.cantidad_en_pedido += cantidad
            stock_pedido.save()

            print("Pedido creado exitosamente.")
            return JsonResponse({
                'mensaje': 'Pedido agregado exitosamente.',
                'pedido': {
                    'id': nuevo_pedido.id,
                    'producto_id': nuevo_pedido.producto_id,
                    'cantidad': nuevo_pedido.cantidad,
                    'fecha_pedido': nuevo_pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'stock_en_pedido': stock_pedido.cantidad_en_pedido
            })

        except Exception as e:
            print(f"Error procesando el pedido: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def obtener_pedidos(request):
    """
    Devuelve un diccionario con los totales de pedidos por producto_id.
    """
    try:
        # Obtener todos los registros en StockEnPedido y sumar los pedidos por producto_id
        pedidos = StockEnPedido.objects.values('producto_id').annotate(total_pedido=models.Sum('cantidad_en_pedido'))
        pedidos_dict = {pedido['producto_id']: pedido['total_pedido'] for pedido in pedidos}

        return JsonResponse({'pedidos': pedidos_dict}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def obtener_pedidos_completo(request):
    """
    View para obtener la lista completa de pedidos con todos los detalles.
    """
    pedidos = Pedido.objects.all().values(
        'id', 'producto_id', 'cantidad', 'proveedor', 'estado', 'fecha_pedido', 'fecha_entrega'
    )
    pedidos_list = []
    for pedido in pedidos:
        pedidos_list.append({
            'id': pedido['id'],
            'producto_id': pedido['producto_id'],
            'cantidad': pedido['cantidad'],
            'proveedor': pedido['proveedor'],
            'estado': pedido['estado'],
            'fecha_pedido': pedido['fecha_pedido'].strftime('%Y-%m-%d %H:%M:%S') if pedido['fecha_pedido'] else None,
            'fecha_entrega': pedido['fecha_entrega'].strftime('%Y-%m-%d %H:%M:%S') if pedido['fecha_entrega'] else None,
        })
    return JsonResponse({'pedidos': pedidos_list})


@csrf_exempt
@login_required
def marcar_entregado(request, pedido_id):
    """
    Vista para marcar un pedido como entregado y actualizar StockEnPedido.
    """
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id)

            if pedido.estado == 'entregado':
                return JsonResponse({'error': 'El pedido ya está marcado como entregado.'}, status=400)

            # Actualizar el estado y la fecha de entrega
            pedido.estado = 'entregado'
            pedido.fecha_entrega = now()
            pedido.save()

            # Actualizar el stock en pedidos
            stock_pedido = StockEnPedido.objects.get(producto_id=pedido.producto_id)
            stock_pedido.cantidad_en_pedido -= pedido.cantidad
            if stock_pedido.cantidad_en_pedido <= 0:
                stock_pedido.delete()
            else:
                stock_pedido.save()

            return JsonResponse({
                'mensaje': f'Pedido {pedido_id} marcado como entregado exitosamente.',
                'producto_id': pedido.producto_id,
                'cantidad_actualizada': stock_pedido.cantidad_en_pedido if stock_pedido.pk else 0
            })
        except Pedido.DoesNotExist:
            return JsonResponse({'error': 'El pedido no existe.'}, status=404)
        except StockEnPedido.DoesNotExist:
            return JsonResponse({'error': 'No existe registro en StockEnPedido para este producto.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
@login_required
def registrar_salida(request, pedido_id):
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id, estado='entregado')

            # Registrar la salida
            MovimientoInventario.objects.create(
                producto_id=pedido.producto_id,
                tipo='salida',
                cantidad=pedido.cantidad,
                fecha=now(),
                sucursal_id=1,  # Cambia a la sucursal correspondiente
                pedido=pedido
            )

            return JsonResponse({
                'mensaje': f'Pedido {pedido_id} enviado a sucursal exitosamente.',
                'producto_id': pedido.producto_id,
                'cantidad': pedido.cantidad
            })
        except Pedido.DoesNotExist:
            return JsonResponse({'error': 'El pedido no existe o no está marcado como entregado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)



@login_required
def obtener_movimientos(request):
    """
    Devuelve los movimientos de inventario filtrados por tipo, fechas o todos.
    """
    if request.method == 'GET':
        try:
            # Obtener los parámetros de consulta
            tipo = request.GET.get('tipo', None)  # 'entrada', 'salida' o None
            fecha_inicio = request.GET.get('fecha_inicio', None)
            fecha_fin = request.GET.get('fecha_fin', None)

            # Base QuerySet
            movimientos = MovimientoInventario.objects.all()

            # Filtrar por tipo si está presente
            if tipo in ['entrada', 'salida']:
                movimientos = movimientos.filter(tipo=tipo)

            # Filtrar por rango de fechas si están presentes
            if fecha_inicio and fecha_fin:
                movimientos = movimientos.filter(
                    fecha__range=[fecha_inicio, fecha_fin]
                )

            # Construir la respuesta
            data = [
                {
                    'id': movimiento.id,
                    'producto_id': movimiento.producto_id,
                    'tipo': movimiento.tipo,
                    'cantidad': movimiento.cantidad,
                    'fecha': movimiento.fecha,
                    'sucursal_id': movimiento.sucursal_id,
                    'pedido_id': movimiento.pedido.id if movimiento.pedido else None,
                }
                for movimiento in movimientos
            ]

            return JsonResponse({'movimientos': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@csrf_exempt
@login_required
def registrar_entrada(request, pedido_id):
    """
    Vista para registrar una entrada en el inventario al marcar un pedido como entregado.
    """
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id, estado='entregado')

            # Registrar la entrada
            movimiento = MovimientoInventario.objects.create(
                producto_id=pedido.producto_id,
                tipo='entrada',
                cantidad=pedido.cantidad,
                fecha=now(),
                sucursal_id=1,  # Cambiar a la sucursal correspondiente
                pedido=pedido
            )

            return JsonResponse({
                'mensaje': f'Entrada registrada exitosamente para el pedido {pedido_id}.',
                'movimiento_id': movimiento.id
            }, status=201)

        except Pedido.DoesNotExist:
            return JsonResponse({'error': 'El pedido no existe o no está marcado como entregado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def ver_productos(request):
    # Agregar logs de depuración
    print(f"Usuario actual: {request.user.username}")
    print(f"Grupos del usuario: {[group.name for group in request.user.groups.all()]}")
    
    # Verificar si el usuario pertenece al grupo Administrador
    if not request.user.groups.filter(name="Administrador").exists():
        print("Redirigiendo a /pos/ - No es administrador")
        return redirect('/pos/')
    
    print("Cargando página de productos - Es administrador")
    return render(request, 'inventory/ver_productos.html')

@login_required
def usuario_actual(request):
    """
    Retorna información sobre el usuario actual.
    """
    is_administrador = request.user.groups.filter(name="Administrador").exists()
    return JsonResponse({'is_administrador': is_administrador})