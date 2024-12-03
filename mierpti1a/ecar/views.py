from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from .models import Producto, Carrito, CarritoProducto, Pedido
from .serializers import ProductoSerializer, CarritoSerializer, PedidoSerializer, CarritoProductoSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from decimal import Decimal
from urllib.parse import unquote,urlparse
from django.db import transaction
import re
from django.http import JsonResponse
from django.http import JsonResponse

def check_origin(func):
    def wrap(request, *args, **kwargs):
        # Obtener la URL de la página de donde proviene la solicitud
        referer = request.META.get('HTTP_REFERER', 'No disponible')
        print(f"Solicitud proveniente de: {referer}")
        path = urlparse(referer).path
        #print(f"Solicitud proveniente de path: {path}")

        allowed_origins = [
            '/ecar/catalogo/',
            '/payments/pagos/',
            '/payments/succesful/',
            '/ecar/carrito/',
        ]

        # Verificar rutas dinámicas y acceso permitido
        if path.startswith('/ecar/producto/') and re.match(r'^/ecar/producto/\d+/$', path):
            return func(request, *args, **kwargs)  # Continuar a la función decorada
        
        if path not in allowed_origins:
            return JsonResponse({'error': 'Acceso no permitido'}, status=403)

        return func(request, *args, **kwargs)  # Continuar a la función decorada
    return wrap

# def check_origin_api(func):
#     def wrap(request, *args, **kwargs):
#         # Obtener la URL de la página de donde proviene la solicitud
#         referer = request.META.get('HTTP_REFERER', 'No disponible')
#         print(f"Solicitud proveniente de: {referer}")
#         path = urlparse(referer).path
#         print(f"Solicitud proveniente de path: {path}")

#         allowed_origins = ['/ecar/catalogo/','/ecar/carrito/',]
#         if path  not in allowed_origins:
#             return JsonResponse({'error': 'Acceso no permitido'}, status=403)
#         return func(request, *args, **kwargs)
#     return wrap

# ----------------------- Vistas para la API REST ----------------------- #

# Vista para productos con soporte para PATCH
class ProductoViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

# Vista para carritos
class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

# Vista para productos en el carrito
class CarritoProductoViewSet(viewsets.ModelViewSet):
    queryset = CarritoProducto.objects.all()
    serializer_class = CarritoProductoSerializer
    permission_classes = [IsAuthenticated]

# Vista para pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

# API para actualizar cantidad del producto en el carrito
@api_view(['POST'])
@permission_classes([IsAuthenticated])
#@check_origin_api
def actualizar_carrito_api(request):
    item_id = request.data.get('item_id')
    action = request.data.get('action')

    try:
        # Buscar el producto en el carrito
        item = CarritoProducto.objects.get(id=item_id, carrito__usuario=request.user)
        producto = item.producto  # Obtener el producto relacionado

        if action == 'increase':
            # Verificar si hay suficiente stock antes de aumentar la cantidad
            if item.cantidad + 1 > producto.stock:
                return Response(
                    {'success': False, 'message': f"No hay suficiente stock para '{producto.nombre}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.cantidad += 1
            item.save()
        elif action == 'decrease':
            # Reducir la cantidad o eliminar el producto si es 1
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
                return Response(
                    {'success': True, 'message': f"'{producto.nombre}' eliminado del carrito."},
                    status=status.HTTP_200_OK
                )
    except CarritoProducto.DoesNotExist:
        return Response(
            {'success': False, 'message': 'El producto no se encuentra en el carrito.'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({'success': True, 'message': f"Cantidad de '{producto.nombre}' actualizada correctamente."})

# API para eliminar un producto del carrito
@api_view(['POST'])
@permission_classes([IsAuthenticated])
#@check_origin_api
def eliminar_del_carrito_api(request):
    item_id = request.data.get('item_id')

    try:
        item = CarritoProducto.objects.get(id=item_id, carrito__usuario=request.user)
        item.delete()
    except CarritoProducto.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'success': True})

# ----------------------- Vistas para el Frontend ----------------------- #
import requests
from django.shortcuts import render
import requests
from django.shortcuts import render
# Vista para mostrar la página de inicio con el catálogo de productos
#@check_origin
@login_required(login_url='/ecar/login/')
def catalogo(request):
    try:
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json()  # Obtener los datos del JSON
            productos = productos_data.get('productos', [])  # Extraer la lista de productos

            # Modificar las rutas de las imágenes y calcular el precio con descuento
            for producto in productos:
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')

                # Cálculo del precio con descuento
                try:
                    precio = Decimal(producto['precio_unitario'])
                    descuento = Decimal(producto['descuento'])
                    if descuento > 0:
                        descuento_decimal = descuento / Decimal(100)
                        producto['precio_con_descuento'] = round(precio * (1 - descuento_decimal), 2)
                    else:
                        producto['precio_con_descuento'] = precio
                except (KeyError, ValueError, TypeError) as e:
                    print(f"Error al calcular el precio con descuento: {e}")
                    producto['precio_con_descuento'] = producto.get('precio_unitario', '0.00')
        else:
            productos = []  # En caso de error en la respuesta, dejar los productos vacíos
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los productos: {e}")
        productos = []

    try:
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json()  # Obtener los datos del JSON
            productos = productos_data.get('productos', [])  # Extraer la lista de productos

            # Modificar las rutas de las imágenes y calcular el precio con descuento
            for producto in productos:
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')

                # Cálculo del precio con descuento
                try:
                    precio = Decimal(producto['precio_unitario'])
                    descuento = Decimal(producto['descuento'])
                    if descuento > 0:
                        descuento_decimal = descuento / Decimal(100)
                        producto['precio_con_descuento'] = round(precio * (1 - descuento_decimal), 2)
                    else:
                        producto['precio_con_descuento'] = precio
                except (KeyError, ValueError, TypeError) as e:
                    print(f"Error al calcular el precio con descuento: {e}")
                    producto['precio_con_descuento'] = producto.get('precio_unitario', '0.00')
        else:
            productos = []  # En caso de error en la respuesta, dejar los productos vacíos
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los productos: {e}")
        productos = []

    return render(request, 'ecar/catalogo.html', {'productos': productos})


# Vista para mostrar los detalles de un producto
@check_origin
@login_required(login_url='/ecar/login/')
def detalle_producto(request, producto_id):
    try:
        # Obtener los datos de la API
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json()
            productos = productos_data.get('productos', [])
            for producto in productos:
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')
            # Buscar el producto por su ID
            producto = next((p for p in productos if p['id'] == int(producto_id)), None)
        else:
            producto = None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el producto: {e}")
        producto = None

    if producto is None:
        return redirect('catalogo')

    # Calcular el precio con descuento directamente en el diccionario
    try:
        precio = Decimal(producto['precio_unitario'])
        descuento = Decimal(producto['descuento'])
        if descuento > 0:
            descuento_decimal = descuento / Decimal(100)
            producto['precio_con_descuento'] = round(precio * (1 - descuento_decimal), 2)
        else:
            producto['precio_con_descuento'] = precio
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error al calcular el precio con descuento: {e}")
        producto['precio_con_descuento'] = producto.get('precio_unitario', '0.00')

    try:
        # Obtener los datos de la API
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json()
            productos = productos_data.get('productos', [])
            for producto in productos:
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')
            # Buscar el producto por su ID
            producto = next((p for p in productos if p['id'] == int(producto_id)), None)
        else:
            producto = None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el producto: {e}")
        producto = None

    if producto is None:
        return redirect('catalogo')

    # Calcular el precio con descuento directamente en el diccionario
    try:
        precio = Decimal(producto['precio_unitario'])
        descuento = Decimal(producto['descuento'])
        if descuento > 0:
            descuento_decimal = descuento / Decimal(100)
            producto['precio_con_descuento'] = round(precio * (1 - descuento_decimal), 2)
        else:
            producto['precio_con_descuento'] = precio
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error al calcular el precio con descuento: {e}")
        producto['precio_con_descuento'] = producto.get('precio_unitario', '0.00')

    return render(request, 'ecar/detalle_producto.html', {'producto': producto})

# Vista para mostrar el carrito de compras
@check_origin
@login_required(login_url='/ecar/login/')
def carrito(request):
    referer = request.GET.get('referer', '')
    empleado_json = request.COOKIES.get('empleado')
    # empleado_decoded = unquote(empleado_json)
    print(f"Debug: mi empleado: {empleado_json}")

    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    productos_carrito = CarritoProducto.objects.filter(carrito=carrito)

    # Obtener información actualizada de los productos desde la API
    try:
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json().get('productos', [])
            productos_dict = {}
            for producto in productos_data:
                # Ajustar la URL de la imagen
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')
                productos_dict[producto['id']] = producto  # Crear un diccionario por ID
        else:
            productos_dict = {}
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los productos desde la API: {e}")
        productos_dict = {}

    # Generar la lista de productos en el carrito combinando datos de la API y del carrito
    carrito_actualizado = []
    for item in productos_carrito:
        producto_api = productos_dict.get(item.producto.id)  # Buscar el producto en la API por ID
        if producto_api:
            carrito_actualizado.append({
                'id': item.id,
                'producto_id': item.producto.id,
                'nombre': producto_api.get('nombre', 'Producto no disponible'),
                'cantidad': item.cantidad,
                'precio_unitario': Decimal(producto_api.get('precio_unitario', 0)),
                'descuento': Decimal(producto_api.get('descuento', 0)),
                'imagen': producto_api.get('imagen', ''),  # Imagen procesada
                'precio_con_descuento': (
                    Decimal(producto_api.get('precio_unitario', 0)) *
                    (1 - Decimal(producto_api.get('descuento', 0)) / 100)
                ).quantize(Decimal('0.01')),  # Calcular precio con descuento y redondear
            })

    # Obtener información actualizada de los productos desde la API
    try:
        response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
        if response.status_code == 200:
            productos_data = response.json().get('productos', [])
            productos_dict = {}
            for producto in productos_data:
                # Ajustar la URL de la imagen
                producto['imagen'] = producto['imagen'].replace('pos/static/img/', '')
                productos_dict[producto['id']] = producto  # Crear un diccionario por ID
        else:
            productos_dict = {}
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los productos desde la API: {e}")
        productos_dict = {}

    # Generar la lista de productos en el carrito combinando datos de la API y del carrito
    carrito_actualizado = []
    for item in productos_carrito:
        producto_api = productos_dict.get(item.producto.id)  # Buscar el producto en la API por ID
        if producto_api:
            # Mezclar los datos del carrito con los datos actualizados de la API
            carrito_actualizado.append({
                'id': item.id,
                'producto_id': item.producto.id,
                'nombre': producto_api.get('nombre', 'Producto no disponible'),
                'cantidad': item.cantidad,
                'precio_unitario': Decimal(producto_api.get('precio_unitario', 0)),
                'descuento': Decimal(producto_api.get('descuento', 0)),
                'imagen': producto_api.get('imagen', ''),  # Imagen procesada
                'precio_con_descuento': (
                    Decimal(producto_api.get('precio_unitario', 0)) *
                    (1 - Decimal(producto_api.get('descuento', 0)) / 100)
                ).quantize(Decimal('0.01')),  # Calcular precio con descuento y redondear
            })

    # Calcular el total del carrito
    total = sum(
        item['precio_con_descuento'] * item['cantidad']
        for item in carrito_actualizado
    )
    total = sum(
        item['precio_con_descuento'] * item['cantidad']
        for item in carrito_actualizado
    )

    return render(request, 'ecar/carrito.html', {
        'productos_carrito': carrito_actualizado,
        'productos_carrito': carrito_actualizado,
        'total': total
    })

@check_origin
@login_required(login_url='/ecar/login/')
def agregar_al_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = request.POST.get('cantidad')

        # Validar datos
        if not producto_id or not cantidad:
            return JsonResponse({'success': False, 'message': 'Producto o cantidad no especificados.'})

        try:
            cantidad = int(cantidad)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Cantidad inválida.'})

        try:
            # Consultar la API para obtener los datos del producto
            response = requests.get('http://127.0.0.1:8000/pos/api_productos/')
            if response.status_code == 200:
                productos = response.json().get('productos', [])
                producto_data = next((p for p in productos if p['id'] == int(producto_id)), None)
                if not producto_data:
                    return JsonResponse({'success': False, 'message': f"Producto con ID {producto_id} no encontrado."})

                # Obtener o crear el producto en la base de datos local
                with transaction.atomic():
                    producto, _ = Producto.objects.update_or_create(
                        id=producto_id,
                        defaults={
                            'nombre': producto_data['nombre'],
                            'stock': producto_data['stock'],
                            'precio': Decimal(producto_data['precio_unitario']),
                            'descuento': Decimal(producto_data['descuento']),
                        },
                    )

                # Verificar stock disponible
                if producto.stock < cantidad:
                    return JsonResponse({'success': False, 'message': f"No hay suficiente stock disponible para '{producto.nombre}'."})

            else:
                return JsonResponse({'success': False, 'message': "No se pudo obtener la lista de productos desde la API."})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'success': False, 'message': f"Error al consultar la API: {e}"})

        # Obtener o crear el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)

        # Obtener o crear la relación en CarritoProducto
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
        )

        if not created:
            if carrito_producto.cantidad + cantidad > producto.stock:
                return JsonResponse({'success': False, 'message': f"No puedes agregar más de {producto.stock} unidades de '{producto.nombre}'."})
            carrito_producto.cantidad += cantidad
        else:
            carrito_producto.cantidad = cantidad

        carrito_producto.save()
        return JsonResponse({'success': True, 'message': f"Producto '{producto.nombre}' agregado al carrito correctamente."})
    else:
        return JsonResponse({'success': False, 'message': "Método no permitido."})
    
def logout_view(request):
    logout(request)
    return redirect('/ecar/login/')

# ----------------------- Registro de Rutas ----------------------- #

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'carrito-productos', CarritoProductoViewSet)

# Agregar las nuevas APIs para actualizar y eliminar del carrito
from django.urls import path

urlpatterns = [
    path('api/update-cart/', actualizar_carrito_api, name='actualizar_carrito_api'),
    path('api/remove-from-cart/', eliminar_del_carrito_api, name='eliminar_del_carrito_api'),
]

# Añadir las rutas del router
from django.urls import include
urlpatterns += [
    path('api/', include(router.urls)),
]
