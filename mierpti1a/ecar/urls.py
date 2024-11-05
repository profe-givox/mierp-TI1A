from django.urls import path, include
from .views import (
    ProductoViewSet, CarritoViewSet, 
    CarritoProductoViewSet, PedidoViewSet,
    agregar_al_carrito,
    catalogo, detalle_producto, carrito, actualizar_carrito_api, eliminar_del_carrito_api  # Asegúrate de importar las nuevas vistas
)
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

# Definición de rutas con el router de DRF
router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'carrito-productos', CarritoProductoViewSet)
router.register(r'pedidos', PedidoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # Rutas para la API REST
    path('api/agregar-al-carrito/', agregar_al_carrito, name='agregar_al_carrito'),  # Nueva ruta
    path('api/update-cart/', actualizar_carrito_api, name='actualizar_carrito_api'),  # Ruta para actualizar carrito
    path('api/remove-from-cart/', eliminar_del_carrito_api, name='eliminar_del_carrito_api'),  # Ruta para eliminar del carrito
    path('catalogo/', catalogo, name='catalogo'),  # Ruta para la vista del catálogo
    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'),  # Ruta para los detalles del producto
    path('carrito/', carrito, name='carrito'),  # Ruta para el carrito de compras
    path('login/', auth_views.LoginView.as_view(template_name='ecar/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
