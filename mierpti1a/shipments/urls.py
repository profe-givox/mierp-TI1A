# shipments/urls.py
from django.urls import path
from .views import order_list, order_create, order_detail

urlpatterns = [
    path('orders/', order_list, name='order_list'),
    path('orders/create/', order_create, name='order_create'),
    path('orders/<int:pk>/', order_detail, name='order_detail'),
]
