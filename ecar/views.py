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
def actualizar_carrito_api(request):
    item_id = request.data.get('item_id')
    action = request.data.get('action')

    try:
        item = CarritoProducto.objects.get(id=item_id, carrito__usuario=request.user)
        if action == 'increase':
            item.cantidad += 1
            item.save()
        elif action == 'decrease':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
    except CarritoProducto.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'success': True})

# API para eliminar un producto del carrito
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
# Vista para mostrar la página de inicio con el catálogo de productos
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

    return render(request, 'ecar/catalogo.html', {'productos': productos})


# Vista para mostrar los detalles de un producto
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

    return render(request, 'ecar/detalle_producto.html', {'producto': producto})

# Vista para mostrar el carrito de compras
@login_required(login_url='/ecar/login/')
def carrito(request):
    # Obtener el carrito del usuario
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

    return render(request, 'ecar/carrito.html', {
        'productos_carrito': carrito_actualizado,
        'total': total
    })


@login_required(login_url='/ecar/login/')
def agregar_al_carrito(request):
    if request.method == 'POST':
        # Obtener el producto y cantidad de la solicitud POST
        producto_id = request.POST.get('producto_id')
        cantidad = request.POST.get('cantidad')

        # Validar que los valores estén presentes
        if not producto_id or not cantidad:
            return redirect('carrito')

        # Convertir cantidad a entero y manejar errores
        try:
            cantidad = int(cantidad)
        except ValueError:
            return redirect('carrito')

        # Obtener el producto o devolver un error 404 si no existe
        producto = get_object_or_404(Producto, id=producto_id)

        # Obtener o crear el carrito del usuario autenticado
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)

        # Usar el método agregar_producto del carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto
        )
        
        if not created:
            carrito_producto.cantidad += 1
        else:
            carrito_producto.cantidad = 1
        carrito_producto.save()

        # Redirigir al carrito después de actualizar el producto
        return redirect('carrito')
    else:
        return redirect('carrito')
    
def logout_view(request):
    logout(request)
    return redirect('/ecar/login/')

# ----------------------- Registro de Rutas ----------------------- #

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'carrito-productos', CarritoProductoViewSet)
router.register(r'pedidos', PedidoViewSet)

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
