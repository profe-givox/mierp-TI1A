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

# Vista para mostrar la página de inicio con el catálogo de productos
@login_required(login_url='/ecar/login/')
def catalogo(request):
    productos = Producto.objects.all()  # Obtén todos los productos
    return render(request, 'ecar/catalogo.html', {'productos': productos})

# Vista para mostrar los detalles de un producto
@login_required(login_url='/ecar/login/')
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'ecar/detalle_producto.html', {'producto': producto})

# Vista para mostrar el carrito de compras
@login_required(login_url='/ecar/login/')
def carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    productos_carrito = CarritoProducto.objects.filter(carrito=carrito)

    # Calcular el total del carrito
    total = sum(item.producto.precio_con_descuento() * item.cantidad for item in productos_carrito)

    return render(request, 'ecar/carrito.html', {
        'productos_carrito': productos_carrito,
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
