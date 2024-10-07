from django.contrib.auth.views import LoginView
from django.shortcuts import render

class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'

def product_form(request):
    return render(request, 'inventory/product_form.html')

def editar_producto(request):
    return render(request, 'inventory/editar_producto.html')

def eliminar_producto(request):
    return render(request, 'inventory/eliminar_producto.html')

def ventas(request):
    return render(request, 'inventory/ventas.html')

def pedidos(request):
    return render(request, 'inventory/pedidos.html')

def nuevo_pedido(request):
    return render(request, 'inventory/nuevo_pedido.html')

def editar_pedido(request):
    return render(request, 'inventory/editar_pedido.html')

def editar_pedido(request):
    return render(request, 'inventory/editar_pedido.html')

def eliminar_pedido(request):
    return render(request, 'inventory/eliminar_pedido.html')

def ver_productos(request):
    return render(request, 'inventory/ver_productos.html')
