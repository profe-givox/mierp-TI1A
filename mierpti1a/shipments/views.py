from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderHistory, OrderStatus, Route, Address, Sucursal
from .forms import OrderForm, AddressForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .serializers import SucursalSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


@login_required
def order_list(request):
    # Si el usuario es administrador, mostramos todos los pedidos
    if request.user.is_superuser:
        orders = Order.objects.all()
    else:
        # Si no es administrador, mostramos solo los pedidos del usuario logueado
        orders = Order.objects.filter(user=request.user)
    return render(request, 'shipments/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    if request.method == 'POST':
        product = request.POST['product']
        quantity = request.POST['quantity']
        status = request.POST['status']
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        selected_address = request.POST.get('selected_address')

        address = Address.objects.create(
            user=request.user,
            street=selected_address,  # Usa el campo 'street' para la dirección completa
            city="Ciudad por definir",
            state="Estado por definir",
            postal_code="00000",
            latitude=latitude,
            longitude=longitude
        )

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            status=status,
            address=address
        )

        return redirect('shipments:order_list')
    return render(request, 'shipments/order_create.html')



@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            # Registrar el cambio de estado
            OrderHistory.objects.create(order=order, status=order.status, changed_at=timezone.now())
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'shipments/order_update.html', {'form': form, 'order': order})

@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'shipments/order_detail.html', {'order': order})

@login_required
def route_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Supón que Route tiene un campo order para vincularlo con Order
    route = get_object_or_404(Route, order=order)
    return render(request, 'shipments/route_detail.html', {'order': order, 'route': route})

@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'shipments/order_edit.html', {'form': form})


@login_required
def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')  # Redirige a la lista de pedidos después de eliminar
    return render(request, 'shipments/order_confirm_delete.html', {'order': order})


@login_required
def listar_sucursales(request):
    sucursales = Sucursal.objects.all()
    sucursales_json = json.dumps(list(sucursales.values('id', 'nombre', 'direccion', 'ciudad', 'estado', 'latitud', 'longitud')))
    return render(request, 'shipments/sucursales_list.html', {'sucursales': sucursales, 'sucursales_json': sucursales_json})

@login_required
@user_passes_test(lambda u: u.is_superuser)
@csrf_exempt
def agregar_sucursal(request):
    if request.method == 'GET':
        return render(request, 'shipments/agregar_sucursal.html')
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        serializer = SucursalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    
@csrf_exempt  # Asegúrate de que esté configurado correctamente para pruebas
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_sucursal(request, pk):
    if request.method == 'DELETE':
        try:
            sucursal = Sucursal.objects.get(pk=pk)
            sucursal.delete()
            return JsonResponse({'message': 'Sucursal eliminada correctamente'}, status=200)
        except Sucursal.DoesNotExist:
            return JsonResponse({'error': 'Sucursal no encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
