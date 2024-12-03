from datetime import timezone
from django.http import HttpResponseForbidden
from urllib.parse import unquote
import json
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import transaction, IntegrityError
from pos.models import Empleado as EmpleadoPos
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.http import HttpResponse

import requests 

## Funcion para verificar puesto de caja TEST1
def verificar_acceso(view_func):
    def wrapper(request, *args, **kwargs):
        # Leer la cookie 'empleado'
        empleado_json = request.COOKIES.get('empleado')
        
        if not empleado_json:
            print("Debug: No se encontró la cookie 'empleado'.")
            return HttpResponseForbidden("Acceso denegado: No se encontraron datos de empleado.")
        
        try:
            # Decodificar la cookie para convertirla de formato URL
            empleado_decoded = unquote(empleado_json)
            print(f"Debug: Empleado decodificado: {empleado_decoded}")

            # Convertir el JSON decodificado a un diccionario de Python
            empleado = json.loads(empleado_decoded)
            print(f"Debug: Información del empleado: {empleado}")
        except json.JSONDecodeError:
            print("Debug: Error al decodificar los datos del empleado.")
            return HttpResponseForbidden("Acceso denegado: Error en los datos del empleado.")
        
        # Obtener y procesar el puesto del empleado
        puesto_completo = empleado.get('puesto', '')
        puesto = puesto_completo.split(' ')[0] if puesto_completo else None
        print(f"Debug: Puesto completo: '{puesto_completo}', Puesto procesado: '{puesto}'")

        # Asignar permisos según el rol del empleado
        vista = view_func.__name__
        print(f"Debug: Accediendo a la vista: {vista}")
        
        # Permisos para "El Patron"
        if puesto == "El":
            print("Debug: Acceso permitido para 'El Patron'.")
            return view_func(request, *args, **kwargs)

        # Permisos para "Caja"
        if puesto == "Caja" and vista in ["venta","realizar_venta"]:
            print("Debug: Acceso permitido para empleado de Caja.")
            return view_func(request, *args, **kwargs)

        # Permisos para "Administrador"
        if puesto == "Administrador" and vista in ["ventasRealizadas", "productos","realizar_venta"]:
            print("Debug: Acceso permitido para Administrador.")
            return view_func(request, *args, **kwargs)

        # Acceso denegado
        print("Debug: Acceso denegado para el puesto actual y la vista solicitada.")
        return HttpResponseForbidden("Acceso denegado: Usuario no autorizado para esta vista.")
    return wrapper

###### Vista de Inicio de sesión con identificación implementada con Django y su función authenticate ######
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from urllib.parse import unquote
import json

def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Inicia sesión
            login(request, user)
            
            # Verificar la cookie 'empleado' para redirigir según el rol
            empleado_json = request.COOKIES.get('empleado')
            if empleado_json:
                try:
                    # Decodificar y cargar los datos del empleado
                    empleado_decoded = unquote(empleado_json)
                    empleado = json.loads(empleado_decoded)
                    puesto_completo = empleado.get('puesto', '')
                    puesto = puesto_completo.split(' ')[0] if puesto_completo else None
                    
                    print(f"Debug: Usuario autenticado con el rol: {puesto}")
                    
                    # Redirigir a la vista correspondiente según el rol
                    if puesto == "Administrador":
                        print("Debug: Redirigiendo al CRUD de productos para administrador.")
                        return redirect('http://127.0.0.1:8000/pos/productos/')
                except json.JSONDecodeError:
                    print("Debug: Error al decodificar los datos del empleado.")
                    messages.error(request, "Error al procesar los datos del empleado.")
            
            # Redirigir a la vista de ventas por defecto
            return redirect('ventas')
        else:
            # Mensaje de error para credenciales incorrectas
            messages.error(request, 'Credenciales incorrectas. Inténtalo de nuevo.')

    return render(request, 'index.html')  # O 'pos/index.html' si está dentro de una subcarpeta


######## Vistas para el funcionamiento de productos ########
@verificar_acceso
def productos(request):
    print("Debug: Usuario accediendo a la vista de CRUD de productos.")
    productos = Producto.objects.all()
    return render(request, 'administrarProductos.html', {'productos': productos})


def get_productos(request):
    productos = list(Producto.objects.values())

    if len(productos) > 0:
        data = {'message': "Success", 'productos': productos}
    else:
        data = {'message': "Not Found"}
    
    return JsonResponse(data)

def get_producto_por_id(request, producto_id):
    producto = list(Producto.objects.filter(id=producto_id).values())
    
    if len(producto) > 0:
        data = {'message': "Success", 'productos': producto}
    else:
        data = {'message': "Not Found"}
    
    return JsonResponse(data)

def sincronizar_sucursales():
    try:
        response = requests.get("http://localhost:8000/RRHH/get_sucursales/")
        if response.status_code == 200:
            data = response.json()
            if data.get('message') == "Success":
                sucursales_rrhh = data['sucursales']
                for sucursal in sucursales_rrhh:
                    Sucursal.objects.update_or_create(
                        id=sucursal['id'],  # Asegúrate de usar el mismo ID
                        defaults={
                            'nombre': sucursal['nombre'],
                            'direccion': sucursal['direccion'],  # O cualquier otro campo que tengas
                        }
                    )
                print("Sucursales sincronizadas exitosamente.")
            else:
                print("No se encontraron sucursales en RRHH.")
        else:
            print("Error al obtener sucursales:", response.status_code)
    except Exception as e:
        print("Error al sincronizar sucursales:", e)
        
def importar_empleados_desde_rrhh(request):
    try:
        # URL de la API en RRHH
        rrhh_url = "http://localhost:8000/RRHH/get_empleados/"

        # Realiza la solicitud GET para obtener los datos de empleados
        response = requests.get(rrhh_url)

        # Verifica si la solicitud fue exitosa
        if response.status_code != 200:
            return JsonResponse({'error': 'No se pudo obtener la lista de empleados desde RRHH'}, status=response.status_code)

        # Decodifica la respuesta JSON
        empleados_rrhh = response.json()

        # Verificar el formato de la respuesta
        print(empleados_rrhh)  # Para depurar y verificar el formato

        # Asegurarse de que 'empleados' sea una lista de diccionarios
        empleados_rrhh = empleados_rrhh.get('empleados', [])  # Ajustar según la estructura real de la respuesta

        # Mapeos entre RRHH y POS
        sucursal_mapping = {
            1: EmpleadoPos.Sucursal.URIANGATO,
            2: EmpleadoPos.Sucursal.PURUANDIRO,
            3: EmpleadoPos.Sucursal.YURIRIA,
        }
        rol_mapping = {
            1: EmpleadoPos.Rol.ADMINISTRADOR,
            2: EmpleadoPos.Rol.EMPLEADO,
            3: EmpleadoPos.Rol.GERENTE,
            4: EmpleadoPos.Rol.SUPERVISOR,
        }

        empleados_importados = 0

        for empleado in empleados_rrhh:
            if isinstance(empleado, dict):  # Verifica que cada 'empleado' sea un diccionario
                # Obtiene la sucursal y el rol de acuerdo con el ID
                sucursal_pos = sucursal_mapping.get(empleado.get('sucursal_id'), EmpleadoPos.Sucursal.URIANGATO)
                rol_pos = rol_mapping.get(empleado.get('puesto_id'), EmpleadoPos.Rol.EMPLEADO)

                # Verifica si ya existe el empleado en POS para evitar duplicados
                if EmpleadoPos.objects.filter(usuario=empleado['correo'].split('@')[0]).exists():
                    continue

                # Crea el empleado en POS
                EmpleadoPos.objects.create(
                    nombre=f"{empleado['nombre']} {empleado['apellidos']}",
                    usuario=empleado['correo'].split('@')[0],
                    contrasenia=empleado['rfc'],  # Asumiendo RFC como contraseña
                    telefono=empleado['numero'],
                    caja=0,  # Ajusta según tu lógica
                    rol=rol_pos,
                    idsucursal=sucursal_pos,
                )

                empleados_importados += 1
            else:
                print(f"Empleado inesperado: {empleado}")

        return JsonResponse({'message': f"Importación completada. Empleados importados: {empleados_importados}"}, status=201)

    except requests.RequestException as e:
        return JsonResponse({'error': f"Error al conectar con RRHH: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({'error': f"Error inesperado: {str(e)}"}, status=500)

@csrf_exempt
def post_producto(request):
    if request.method == 'POST':
        try:
            sincronizar_sucursales()
            sucursal_id = int(request.POST.get('sucursal'))

            # Validar que la sucursal exista en POS
            if not Sucursal.objects.filter(id=sucursal_id).exists():
                return JsonResponse({'error': 'La sucursal seleccionada no es válida.'}, status=400)

            Producto.objects.create(
                nombre=request.POST.get('nombre'),
                precio_unitario=float(request.POST.get('precio_unitario')),
                descuento=int(request.POST.get('descuento')),
                stock=int(request.POST.get('stock')),
                descripcion=request.POST.get('descripcion'),
                sucursal_id=sucursal_id,
                imagen=request.FILES.get('imagen')
            )

            return JsonResponse({'message': 'Producto agregado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

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
@verificar_acceso
def ventasRealizadas(request):
    print("Debug: Usuario accediendo a la vista de ventas realizadas.")
    return render(request, 'ventasRealizadas.html')

def get_ventasRealizadas(request, sucuarsalid):
    if request.method == "GET":
        sucursal_id = sucuarsalid
        
        if sucursal_id:
            # Filtrar las ventas por la sucursal del usuario
            ventas = list(Venta.objects.filter(sucursal_id=sucursal_id).values(
                'empleado', 'id', 'descripcion', 'total', 'sucursal__nombre'
            ))
            return JsonResponse(ventas, safe=False)
        else:
            return JsonResponse({'error': 'El usuario no tiene una sucursal asignada.'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
@verificar_acceso
def realizar_venta(request):
    if request.method == 'POST':
        try:
            print("Datos recibidos:", request.body)
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
                fecha=data.get('fecha')
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

###### Catálogo de productos en inventario ###### 
def catalogo(request):
    return render(request, 'catalogo.html')

def get_catalogo(request):
    catalogo = list(Producto.objects.values())
    
    if len(catalogo) > 0:
        data = {'message': "Success", 'catalogo': catalogo}
    else:
        data = {'message': "Not Found"}
    
    return JsonResponse(data)

###### Realizar Ventas ###### 
@verificar_acceso
def venta(request):
    print("Debug: Usuario accediendo a la vista de ventas.")
    return render(request, 'ventas.html')

# Control de Usuarios 
def administrarUsuarios(request):
    return render(request, 'administrarUsuarios.html')

# API conexión productos 
def api_products(request):
    productos = list(Producto.objects.values())
    
    if len(productos) > 0:
        data = {'contine': "ta bien", 'productos': productos}
    else:
        data = {'no tiene': "productos"} 
    return JsonResponse(data)

# Parte para generar el vouncher 
def generar_voucher(request, venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
        
        # Crear una respuesta HTTP con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="voucher_{venta_id}.pdf"'

        # Crear el objeto canvas para generar el PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Agregar detalles al PDF (aquí puedes personalizar más)
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 100, f"Voucher de Venta No. {venta_id}")
        p.drawString(100, height - 120, f"Empleado: {venta.empleado.nombre}")
        p.drawString(100, height - 140, f"Sucursal: {venta.sucursal.nombre}")
        p.drawString(100, height - 160, f"Descripción: {venta.descripcion}")
        p.drawString(100, height - 180, f"Total: {venta.total}")
        p.drawString(100, height - 200, f"Fecha: {venta.fecha}")

        p.showPage()  # Finalizar la página
        p.save()  # Guardar el PDF

        return response

    except Venta.DoesNotExist:
        return HttpResponse("Venta no encontrada", status=404)

def generar_reporte_ventas(request):
    try:
        # Obtener todas las ventas
        ventas = Venta.objects.all()

        # Calcular el total neto de todas las ventas
        total_neto = sum(venta.total for venta in ventas)

        # Obtener la sucursal del reporte
        sucursal = "Sucursal Principal"  # Cambia esta línea si tienes lógica para obtener la sucursal

        # Crear una respuesta HTTP con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

        # Crear el objeto canvas para generar el PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Fecha y hora actual
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime("%d/%m/%Y %H:%M:%S")

        # Dibujar el encabezado con el color verde exacto
        verde_empresa = colors.HexColor("#006838")  # Color verde proporcionado
        p.setFillColor(verde_empresa)
        p.rect(0, height - 60, width, 60, fill=True, stroke=False)  # Fondo verde del encabezado

        # Añadir el texto "Paraiso Rangel"
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 40, "Paraiso Rangel")  # Texto del "botón"

        # Añadir el nombre de la sucursal debajo de "Paraiso Rangel"
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 55, f"Sucursal: {sucursal}")

        # Añadir el título del reporte a la derecha
        p.setFont("Helvetica-Bold", 16)
        p.drawString(width - 200, height - 40, "Reporte de Ventas")  # Alineado a la derecha
        p.setFont("Helvetica", 10)
        p.drawString(width - 200, height - 50, f"Generado: {fecha_formateada}")

        # Tabla de ventas
        y_position = height - 120
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.black)
        p.drawString(50, y_position, "Empleado")
        p.drawString(150, y_position, "Venta No")
        p.drawString(250, y_position, "Descripción")
        p.drawString(400, y_position, "Total")
        p.drawString(500, y_position, "Sucursal")

        # Línea debajo del encabezado
        p.line(50, y_position - 5, 550, y_position - 5)

        # Contenido de las ventas
        p.setFont("Helvetica", 10)
        for venta in ventas:
            y_position -= 20
            if y_position < 50:  # Si se queda sin espacio en la página
                p.showPage()  # Crear una nueva página
                y_position = height - 50  # Reiniciar posición en la nueva página

                # Redibujar encabezado en la nueva página
                p.setFillColor(verde_empresa)
                p.rect(0, height - 60, width, 60, fill=True, stroke=False)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 20)
                p.drawString(50, height - 40, "Paraiso Rangel")
                p.setFont("Helvetica", 12)
                p.drawString(50, height - 55, f"Sucursal: {sucursal}")

                p.setFont("Helvetica-Bold", 16)
                p.drawString(width - 200, height - 40, "Reporte de Ventas")
                p.setFont("Helvetica", 10)
                p.drawString(width - 200, height - 50, f"Generado: {fecha_formateada}")

                # Redibujar la cabecera de la tabla
                y_position = height - 120
                p.setFont("Helvetica-Bold", 10)
                p.setFillColor(colors.black)
                p.drawString(50, y_position, "Empleado")
                p.drawString(150, y_position, "Venta No")
                p.drawString(250, y_position, "Descripción")
                p.drawString(400, y_position, "Total")
                p.drawString(500, y_position, "Sucursal")
                p.line(50, y_position - 5, 550, y_position - 5)

            # Escribir datos de la venta
            p.drawString(50, y_position, venta.empleado.nombre)
            p.drawString(150, y_position, str(venta.id))
            p.drawString(250, y_position, venta.descripcion[:20])  # Cortar descripción si es muy larga
            p.drawString(400, y_position, f"${venta.total}")
            p.drawString(500, y_position, venta.sucursal.nombre)

        # Añadir el Total Neto al final de la tabla
        y_position -= 40
        if y_position < 50:  # Si no hay espacio suficiente para "Total Neto"
            p.showPage()
            y_position = height - 50

            # Redibujar encabezado en la nueva página
            p.setFillColor(verde_empresa)
            p.rect(0, height - 60, width, 60, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, height - 40, "Paraiso Rangel")
            p.setFont("Helvetica", 12)
            p.drawString(50, height - 55, f"Sucursal: {sucursal}")

            p.setFont("Helvetica-Bold", 16)
            p.drawString(width - 200, height - 40, "Reporte de Ventas")
            p.setFont("Helvetica", 10)
            p.drawString(width - 200, height - 50, f"Generado: {fecha_formateada}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(400, y_position, f"Total Neto: ${total_neto:.2f}")  # Mostrar el total neto
        p.showPage()
        p.save()

        return response

    except Exception as e:
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)