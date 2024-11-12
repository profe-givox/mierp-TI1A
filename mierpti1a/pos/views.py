from datetime import timezone
import json
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import get_object_or_404


from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import transaction   

#import requests

###### Vista de Inicio de secion con identificacion implementada con Django y su funcion Autenticate ######
def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('ventas')
        else:
            messages.error(request, 'Credenciales incorrectas. Inténtalo de nuevo.')

    return render(request, 'pos/templates/index.html')


######## Vistas para el funcionamiento de productos ########
def productos(request):
    return render(request, 'pos/templates/administrarProductos.html')

def get_productos(request):
    productos = list(Producto.objects.values())

    if (len(productos)>0):
        data = {'message':"Success", 'productos':productos}
    else:
        data = {'message':"Not Found"}
    
    return JsonResponse(data)

def get_producto_por_id(request, producto_id):
    producto = list(Producto.objects.filter(id=producto_id).values())
    
    if (len(producto)>0):
        data = {'message':"Success", 'productos':producto}
    else:
        data = {'message':"Not Found"}
    
    return JsonResponse(data)

@csrf_exempt
def post_producto(request):
    if request.method == 'POST':
        try:
            # Extraer datos directamente desde request.POST y request.FILES
            Nombre = request.POST.get('nombre')
            Precio = float(request.POST.get('precio_unitario'))  # Convertir a float
            Descuento = int(request.POST.get('descuento'))       # Convertir a entero
            Stock = int(request.POST.get('stock'))               # Convertir a entero
            Descripcion = request.POST.get('descripcion')
            Sucursal_id = request.POST.get('sucursal')
            
            # Extraer el archivo de imagen desde request.FILES
            imagen_producto = request.FILES.get('imagen')

            # Verificar que la sucursal existe
            sucursal_obj = Sucursal.objects.filter(id=Sucursal_id).first()
            if not sucursal_obj:
                return JsonResponse({'error': 'Sucursal no encontrada'}, status=400)

            # Crear el producto
            Producto.objects.create(
                nombre=Nombre, 
                precio_unitario=Precio, 
                descuento=Descuento, 
                stock=Stock, 
                descripcion=Descripcion, 
                sucursal=sucursal_obj,
                imagen=imagen_producto
            )
            
            return JsonResponse({'message': 'Producto agregado con éxito'})
        
        except ValueError as e:
            return JsonResponse({'error': 'Error en los tipos de datos: ' + str(e)}, status=400)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def edit_producto(request, producto_id):
    if request.method == 'POST':  # Cambiar a POST si se usa FormData
        producto = get_object_or_404(Producto, id=producto_id)

        try:
            # Extraer datos de request.POST y request.FILES
            producto.nombre = request.POST.get('nombre')
            producto.precio_unitario = float(request.POST.get('precio_unitario'))  # Convertir a float
            producto.descuento = int(request.POST.get('descuento'))                # Convertir a int
            producto.stock = int(request.POST.get('stock'))                        # Convertir a int
            producto.descripcion = request.POST.get('descripcion')

            sucursal_id = request.POST.get('sucursal')
            producto.sucursal = get_object_or_404(Sucursal, id=sucursal_id)        # Verificar si la sucursal existe

            # Si hay una nueva imagen, actualízala
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']

            # Guardar los cambios en el producto
            producto.save()
            print("Guardando producto:", producto.id)

            return JsonResponse({'message': 'Producto editado con éxito'})
        
        except ValueError as e:
            return JsonResponse({'error': 'Error en los tipos de datos: ' + str(e)}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def borrar_producto(request, producto_id):
    if request.method == 'DELETE':
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        return JsonResponse({'message': 'Producto borrado con éxito'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)



#### Vistas para el funcionamiento de Ventas Realizadas ####
def ventasRealizadas(request):
    return render(request, 'pos/templates/ventasRealizadas.html')

def get_ventasRealizadas(request):
    if request.method == "GET":
        ventas = list(Venta.objects.values('empleado', 'id', 'descripcion', 'total', 'sucursal'))
        return JsonResponse(ventas, safe=False)
    
@csrf_exempt
def realizar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Verificación de campos
            descripcion = data.get('descripcion')
            total = data.get('total')
            empleado_id = data.get('empleado_id')
            sucursal_id = data.get('sucursal_id')

            if not all([descripcion, total, empleado_id, sucursal_id]):
                return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)

            empleado = Empleado.objects.get(id=empleado_id)
            sucursal = Sucursal.objects.get(id=sucursal_id)

            # Crear la venta con la fecha actual
            venta = Venta.objects.create(
                empleado=empleado,
                sucursal=sucursal,
                descripcion=descripcion,
                total=total,
                fecha = data.get('fecha')
            )

            return JsonResponse({'message': 'Venta registrada exitosamente'}, status=201)

        except Empleado.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except Sucursal.DoesNotExist:
            return JsonResponse({'error': 'Sucursal no encontrada'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

###### Catalago de productos en inventario ###### 
def catalogo(request):
    return render(request, 'pos/templates/catalogo.html')

def get_catalogo(request):
    catalogo = list(Producto.objects.values())
    
    if (len(catalogo)>0):
        data = {'message':"Success", 'catalogo':catalogo}
    else:
        data = {'message':"Not Found"}
    
    return JsonResponse(data)

###### Realizar Ventas ###### 
def venta(request):
    return render(request, 'pos/templates/ventas.html')


#Control de Usuarios 
def administrarUsuarios(request):
    return render(request, 'pos/templates/administrarUsuarios.html')

# api conexion productos 
def api_products(request):
    productos =list(Producto.objects.values())
    
    if (len(productos)>0):
        data = {'contine': "ta bien", 'productos':productos}
            
    else:
        data = {'no tiene':"productos"} 
    return JsonResponse(data)



# Conexión con recursos humanos 
#def login(request):
    if request.method == 'POST':
        # Recoger los datos del formulario o de la solicitud
        folio = request.POST.get('folio')
        password = request.POST.get('password')

        # Define la URL de la API
        url = "http://localhost:8000/RRHH/login/"

        # Define los datos que quieres enviar en la solicitud POST
        data = {
            "folio": folio,
            "action": "login",
            "password": password
        }

        # Realiza la solicitud POST
        response = requests.post(url, json=data)

        # Procesa la respuesta de la API
        if response.status_code == 200:
            resultado = response.json()
            return JsonResponse({'status': 'success', 'data': resultado})
        else:
            return JsonResponse({'status': 'error', 'message': response.json()})
    return render(request, 'index.html')
