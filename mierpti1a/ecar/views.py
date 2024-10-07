from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import Producto, Carrito, CarritoProducto, Pedido
from .serializers import ProductoSerializer, CarritoSerializer, PedidoSerializer, CarritoProductoSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# ----------------------- Vistas para la API REST ----------------------- #

# Vista para productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# Vista para carritos
class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

# Vista para productos en el carrito
class CarritoProductoViewSet(viewsets.ModelViewSet):
    queryset = CarritoProducto.objects.all()
    serializer_class = CarritoProductoSerializer

# Vista para pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

# ----------------------- Vistas para el Frontend ----------------------- #

# Vista para mostrar la página de inicio con el catálogo de productos
def catalogo(request):
    productos = Producto.objects.all()  # Obtén todos los productos
    return render(request, 'ecar/catalogo.html', {'productos': productos})

# Vista para mostrar los detalles de un producto
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'ecar/detalle_producto.html', {'producto': producto})

# Vista para mostrar el carrito de compras
def carrito(request):
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        productos_carrito = CarritoProducto.objects.filter(carrito=carrito)

        # Calcular el total del carrito
        total = sum(item.producto.precio * item.cantidad for item in productos_carrito)
    else:
        productos_carrito = []
        total = 0  # Si no hay productos o no está autenticado

    return render(request, 'ecar/carrito.html', {
        'productos_carrito': productos_carrito,
        'total': total
    })


def agregar_al_carrito(request):
    # Obtener el producto y cantidad de la solicitud POST
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))  # Si no se especifica, la cantidad es 1

    # Obtener el producto o devolver un error 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener o crear el carrito del usuario autenticado
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)

    # Usar el método agregar_producto del carrito
    carrito.agregar_producto(producto, cantidad)

    # Responder con un JSON indicando que todo salió bien
    return JsonResponse({'message': 'Producto agregado al carrito correctamente', 'producto_id': producto.id, 'cantidad': cantidad})