# shipments/urls.py
from django.urls import path
from .views import order_list, order_create, order_detail, route_detail

urlpatterns = [
    path('orders/', order_list, name='order_list'),
    path('orders/create/', order_create, name='order_create'),
    path('orders/<int:pk>/', order_detail, name='order_detail'),
    path('orders/<int:pk>/route/', route_detail, name='route_detail'),  # Confirmar que esta ruta esté definida
]

urlpatterns = [
]