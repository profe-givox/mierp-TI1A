from django.urls import path, include
from .views import (
    ProductoViewSet, CarritoViewSet, 
    CarritoProductoViewSet,
    agregar_al_carrito,
    catalogo, detalle_producto, carrito, actualizar_carrito_api, eliminar_del_carrito_api
)
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'carritos', CarritoViewSet)
router.register(r'carrito-producto', CarritoProductoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/agregar-al-carrito/', agregar_al_carrito, name='agregar_al_carrito'),
    path('api/update-cart/', actualizar_carrito_api, name='actualizar_carrito_api'),
    path('api/remove-from-cart/', eliminar_del_carrito_api, name='eliminar_del_carrito_api'),
    path('catalogo/', catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'), 
    path('carrito/', carrito, name='carrito'),
    path('login/', auth_views.LoginView.as_view(template_name='ecar/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
