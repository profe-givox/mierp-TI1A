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
    else:
        productos_carrito = []
    return render(request, 'ecar/carrito.html', {'productos_carrito': productos_carrito})



@api_view(['POST'])
def agregar_al_carrito(request):
    usuario = request.user
    if not usuario.is_authenticated:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    producto_id = request.data.get('producto')
    cantidad = request.data.get('cantidad', 1)

    try:
        producto = Producto.objects.get(id=producto_id)
        carrito, created = Carrito.objects.get_or_create(usuario=usuario)

        # Agregar o actualizar la cantidad del producto en el carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(carrito=carrito, producto=producto)

        # Si el producto ya estaba en el carrito, actualiza la cantidad
        carrito_producto.cantidad += cantidad
        carrito_producto.save()

        return Response({'mensaje': 'Producto agregado al carrito'}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)