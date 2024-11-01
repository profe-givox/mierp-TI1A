from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderHistory, OrderStatus, Route, Address
from .forms import OrderForm, AddressForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required


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