from django.urls import path, include
from .views import (
    ProductoViewSet, CarritoViewSet, 
    CarritoProductoViewSet, PedidoViewSet,
    agregar_al_carrito,
    catalogo, detalle_producto, carrito  # Asegúrate de importar tus vistas
)
from rest_framework.routers import DefaultRouter

# Definición de rutas con el router de DRF
router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'carrito-productos', CarritoProductoViewSet)
router.register(r'pedidos', PedidoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # Rutas para la API REST
    path('api/agregar-al-carrito/', agregar_al_carrito, name='agregar_al_carrito'),  # Nueva ruta
    path('catalogo/', catalogo, name='catalogo'),  # Ruta para la vista del catálogo
    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'),  # Ruta para los detalles del producto
    path('carrito/', carrito, name='carrito'),  # Ruta para el carrito de compras
]
