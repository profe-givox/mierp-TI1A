# shipments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order

# Vista para mostrar la lista de pedidos
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'shipments/order_list.html', {'orders': orders})

# Vista para crear un nuevo pedido
def order_create(request):
    if request.method == 'POST':
        product = request.POST.get('product')
        customer_name = request.POST.get('customer_name')
        delivery_address = request.POST.get('delivery_address')
        new_order = Order.objects.create(
            product=product,
            customer_name=customer_name,
            delivery_address=delivery_address,
            status='Pending'
        )
        return redirect('order_list')
    return render(request, 'shipments/order_create.html')

# Vista para ver el detalle de un pedido específico
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'shipments/order_detail.html', {'order': order})
