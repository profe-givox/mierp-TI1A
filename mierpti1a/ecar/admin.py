from django.contrib import admin
from .models import Producto, Carrito, CarritoProducto, Pedido

# Registro de modelos en el admin de Django
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(CarritoProducto)
admin.site.register(Pedido)