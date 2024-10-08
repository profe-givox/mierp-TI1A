from django.urls import path, include
from .views import CustomLoginView, product_form, editar_producto, eliminar_producto, ventas, pedidos, nuevo_pedido
from .views import editar_pedido, eliminar_pedido, ver_productos

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('productos/agregar/', product_form, name='product_form'),
    path('productos/editar/', editar_producto, name='editar_producto'),
    path('productos/eliminar/', eliminar_producto, name='eliminar_producto'),
    path('productos/ventas/', ventas, name='ventas'),
    path('productos/pedidos/', pedidos, name='pedidos'),
    path('pedido/nuevo/', nuevo_pedido, name='nuevo_pedido'),
    path('pedido/editar/', editar_pedido, name='editar_pedido'), 
    path('pedido/eliminar/', eliminar_pedido, name='eliminar_pedido'),
    path('productos/', ver_productos, name='ver_productos'),
    # Aquí podrías incluir rutas adicionales si es necesario
    # path('api/', include('rest_framework.urls')), 
]
