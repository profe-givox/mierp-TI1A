import random
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Producto, UbicacionProducto, Almacen
import json
from django.db import models

# Vista personalizada de login
class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'

# Vistas para renderizar las plantillas HTML
def product_form(request):
    return render(request, 'inventory/product_form.html')

def editar_producto(request):
    almacenes = Almacen.objects.all() 
    return render(request, 'inventory/editar_producto.html', {'almacenes': almacenes})


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

def eliminar_pedido(request):
    return render(request, 'inventory/eliminar_pedido.html')

def ver_productos(request):
    return render(request, 'inventory/ver_productos.html')

# API CRUD para Productos

from django.db.models import Prefetch

from django.http import JsonResponse
from django.db.models import Q
from .models import Producto

def buscar_producto(request):
    search_query = request.GET.get('search', '').strip()
    if search_query:
        producto = Producto.objects.filter(
            Q(codigo_producto__icontains=search_query) | Q(nombre_producto__icontains=search_query)
        ).first()

        if producto:
            data = {
                'id': producto.id,  # Añadir el ID del producto aquí
                'codigo_producto': producto.codigo_producto,
                'nombre_producto': producto.nombre_producto,
                'proveedor': producto.proveedor,
                'categoria': producto.categoria,
                'cantidad_por_unidad': producto.cantidad_por_unidad,
                'precio_unitario': str(producto.precio_unitario),
                'unidades_en_existencia': producto.unidades_en_existencia,
                'unidades_en_pedido': producto.unidades_en_pedido,
                'nivel_reorden': producto.nivel_reorden,
                'almacen': producto.ubicacionproducto_set.first().almacen.nombre if producto.ubicacionproducto_set.exists() else '',
                'estante': producto.ubicacionproducto_set.first().estante if producto.ubicacionproducto_set.exists() else '',
                'lugar': producto.ubicacionproducto_set.first().lugar if producto.ubicacionproducto_set.exists() else ''
            }
            return JsonResponse({'producto': data})
        else:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'No se proporcionó un término de búsqueda'}, status=400)

# Listar productos con opción de búsqueda
def listar_productos(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')  # Obtener el parámetro de búsqueda
        if search_query:
            # Filtrar productos por código o nombre que coincidan con el criterio de búsqueda
            productos = Producto.objects.filter(
                models.Q(codigo_producto__icontains=search_query) |
                models.Q(nombre_producto__icontains=search_query)
            )
        else:
            productos = Producto.objects.all()

        # Usar Prefetch para traer las ubicaciones y almacenes asociados
        productos = productos.prefetch_related(
            Prefetch(
                'ubicacionproducto_set',
                queryset=UbicacionProducto.objects.select_related('almacen')
            )
        )

        # Construir la respuesta JSON
        productos_data = []
        for producto in productos:
            ubicacion_producto = producto.ubicacionproducto_set.first()  # Asume una ubicación por producto
            productos_data.append({
                'codigo_producto': producto.codigo_producto,
                'nombre_producto': producto.nombre_producto,
                'proveedor': producto.proveedor,
                'categoria': producto.categoria,
                'cantidad_por_unidad': producto.cantidad_por_unidad,
                'precio_unitario': str(producto.precio_unitario),
                'unidades_en_existencia': producto.unidades_en_existencia,
                'unidades_en_pedido': producto.unidades_en_pedido,
                'nivel_reorden': producto.nivel_reorden,
                'almacen': ubicacion_producto.almacen.nombre if ubicacion_producto else '',
                'ubicacion_almacen': ubicacion_producto.almacen.ubicacion if ubicacion_producto else '',
                'estante': ubicacion_producto.estante if ubicacion_producto else '',
                'lugar': ubicacion_producto.lugar if ubicacion_producto else ''
            })

        return JsonResponse({'productos': productos_data})



# Crear producto
from django.db import transaction

@csrf_exempt
def crear_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Verificar si el código de producto ya existe
            codigo_producto = data.get('codigo_producto')
            if Producto.objects.filter(codigo_producto=codigo_producto).exists():
                return JsonResponse({'error': 'Este código de producto ya existe'}, status=400)

            # Iniciar una transacción atómica
            with transaction.atomic():
                # Crear el producto
                producto = Producto.objects.create(
                    codigo_producto=codigo_producto,
                    nombre_producto=data['nombre'],
                    proveedor=data['proveedor'],
                    categoria=data['categoria'],
                    cantidad_por_unidad=data['cantidad_por_unidad'],
                    precio_unitario=data['precio_unitario'],
                    unidades_en_existencia=data['unidades_en_existencia'],
                    unidades_en_pedido=data['unidades_en_pedido'],
                    nivel_reorden=data['nivel_reorden']
                )

                # Verificar si el almacen_id es válido
                almacen_id = data.get('almacen')
                if not almacen_id:
                    raise ValueError('Debes seleccionar un almacén')

                # Crear la ubicación del producto
                almacen = get_object_or_404(Almacen, id=almacen_id)
                UbicacionProducto.objects.create(
                    producto=producto,
                    almacen=almacen,
                    estante=data['estante'],
                    lugar=data['lugar']
                )

            return JsonResponse({'mensaje': 'Producto creado exitosamente', 'producto_id': producto.id}, status=201)

        except Exception as e:
            print(f"Error al crear el producto: {e}")
            return JsonResponse({'error': f'Error al crear el producto: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)




@csrf_exempt
def actualizar_producto(request, producto_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            producto = get_object_or_404(Producto, id=producto_id)
            
            # Actualizar campos del producto
            producto.codigo_producto = data.get('codigo_producto', producto.codigo_producto)
            producto.nombre_producto = data.get('nombre', producto.nombre_producto)
            producto.proveedor = data.get('proveedor', producto.proveedor)
            producto.categoria = data.get('categoria', producto.categoria)
            producto.cantidad_por_unidad = data.get('cantidad_por_unidad', producto.cantidad_por_unidad)
            producto.precio_unitario = data.get('precio_unitario', producto.precio_unitario)
            producto.unidades_en_existencia = data.get('unidades_en_existencia', producto.unidades_en_existencia)
            producto.unidades_en_pedido = data.get('unidades_en_pedido', producto.unidades_en_pedido)
            producto.nivel_reorden = data.get('nivel_reorden', producto.nivel_reorden)
            producto.save()

            # Actualizar ubicación del producto
            almacen_id = data.get('almacen')
            estante = data.get('estante')
            lugar = data.get('lugar')

            if almacen_id:
                almacen = get_object_or_404(Almacen, id=almacen_id)
                ubicacion_producto, created = UbicacionProducto.objects.update_or_create(
                    producto=producto,
                    defaults={
                        'almacen': almacen,
                        'estante': estante,
                        'lugar': lugar
                    }
                )

            return JsonResponse({'mensaje': 'Producto y ubicación actualizados exitosamente'})

        except Exception as e:
            print(f"Error al actualizar el producto: {e}")
            return JsonResponse({'error': f'Error al actualizar el producto: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)





# Eliminar producto
@csrf_exempt
def eliminar_producto_api(request, producto_id):
    if request.method == 'DELETE':
        try:
            producto = get_object_or_404(Producto, id=producto_id)
            producto.delete()
            return JsonResponse({'mensaje': 'Producto eliminado exitosamente'})

        except Exception as e:
            print(f"Error al eliminar el producto: {e}")
            return JsonResponse({'error': 'Error al eliminar el producto'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)







from .models import Producto, Almacen  

def product_form(request):
    almacenes = Almacen.objects.all() 
    return render(request, 'inventory/product_form.html', {'almacenes': almacenes})


