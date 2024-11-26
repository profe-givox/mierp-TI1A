from django.urls import path
from . import views


urlpatterns = [
    ## Vistas HTML
    path('', views.index, name='index'),
    path('productos/', views.productos, name='administrarProductos'),
    path('venta/', views.venta, name='venta'),
    path('ventas/', views.ventasRealizadas, name='ventas'),
    path('catalogo/', views.catalogo, name='catalogo'),
    

    #### Get de Cosas 
    path('catalogo/get_catalogo/', views.get_catalogo, name='Ver catalago de productos'),
    path('ventas/get_ventasRealizadas/', views.get_ventasRealizadas, name='obtenerventas'),
    path('venta/get_productos/<int:producto_id>/', views.get_producto_por_id, name='busquedaVenta'), ## Obtener producto para venta
    path('productos/get_productos/', views.get_productos, name='Ver Productos'),
    path('productos/get_productos/<int:producto_id>/', views.get_producto_por_id, name='Tomar un catalogo por id'),

    ### Post de cosas
    path('productos/agregar_producto/', views.post_producto, name='agregarproducto'),
    path('venta/realizar_venta/', views.realizar_venta, name='guardarnuevaventa'),

    #### CRUDs
    path('productos/borrar_producto/<int:producto_id>/', views.borrar_producto, name='eliminarproducto'),
    path('productos/editar_producto/<int:producto_id>/', views.edit_producto, name='edit_producto'),
    
    #api de productos 
    path('api_productos/', views.api_products, name='apiproducto'),
]  