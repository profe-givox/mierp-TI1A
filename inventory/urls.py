from django.urls import path
from .views import (control_inventarios, gestion_pedidos, control_entradas_salidas, informes_analisis, ver_productos, obtener_pedidos, redirigir_a_productos)
from .views import (agregar_pedido, obtener_pedidos_completo, marcar_entregado, registrar_salida, obtener_movimientos, registrar_entrada, usuario_actual)

urlpatterns = [
    path('control_inventarios/', control_inventarios, name='control_inventarios'),
    path('gestion_pedidos/', gestion_pedidos, name='gestion_pedidos'),
    path('control_entradas_salidas/', control_entradas_salidas, name='control_entradas_salidas'),
    path('informes_analisis/', informes_analisis, name='informes_analisis'),
    path('productos/', ver_productos, name='ver_productos'),  # Ruta para la página de productos
    path('usuario_actual/', usuario_actual, name='usuario_actual'), 


    path('', redirigir_a_productos, name='redirigir_a_productos'),
    path('agregar_pedido/', agregar_pedido, name='agregar_pedido'),
    path('obtener_pedidos/', obtener_pedidos, name='obtener_pedidos'),  # id junto con lo que esta en pedido
    path('obtener_pedidos_completo/', obtener_pedidos_completo, name='obtener_pedidos_completo'),
    path('marcar_entregado/<int:pedido_id>/', marcar_entregado, name='marcar_entregado'),
    path('registrar_salida/<int:pedido_id>/', registrar_salida, name='registrar_salida'),
    path('obtener_movimientos/', obtener_movimientos, name='obtener_movimientos'),
    path('registrar_entrada/<int:pedido_id>/', registrar_entrada, name='registrar_entrada'),
    

]
