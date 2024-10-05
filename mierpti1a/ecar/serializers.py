from rest_framework import serializers
from .models import Producto, Carrito, CarritoProducto, Pedido

# Serializador de Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

# Serializador de CarritoProducto (relación carrito-producto)
class CarritoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoProducto
        fields = '__all__'

# Serializador de Carrito
class CarritoSerializer(serializers.ModelSerializer):
    productos = CarritoProductoSerializer(many=True)

    class Meta:
        model = Carrito
        fields = ['usuario', 'productos']

# Serializador de Pedido
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'