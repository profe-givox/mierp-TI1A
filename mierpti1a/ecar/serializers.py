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
        

        

class CarritoSerializer(serializers.ModelSerializer):
    productos = CarritoProductoSerializer(many=True, source='carritoproducto_set', required=False)
    productos = CarritoProductoSerializer(many=True, source='carritoproducto_set', required=False)

    class Meta:
        model = Carrito
        fields = ['usuario', 'productos']

    def create(self, validated_data):
        productos_data = validated_data.pop('carritoproducto_set', [])
        carrito = Carrito.objects.create(**validated_data)
        
        for producto_data in productos_data:
            producto = producto_data.get('producto')
            cantidad = producto_data.get('cantidad', 1)
            CarritoProducto.objects.create(carrito=carrito, producto=producto, cantidad=cantidad)
        
        return carrito

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('carritoproducto_set', [])
        
        # Actualizar los campos básicos del carrito
        instance.usuario = validated_data.get('usuario', instance.usuario)
        instance.save()

        # Actualizar productos
        for producto_data in productos_data:
            producto = producto_data.get('producto')
            cantidad = producto_data.get('cantidad', 1)

            carrito_producto, created = CarritoProducto.objects.get_or_create(carrito=instance, producto=producto)
            if not created:
                carrito_producto.cantidad = cantidad
            carrito_producto.save()
        
        return instance

    def create(self, validated_data):
        productos_data = validated_data.pop('carritoproducto_set', [])
        carrito = Carrito.objects.create(**validated_data)
        
        for producto_data in productos_data:
            producto = producto_data.get('producto')
            cantidad = producto_data.get('cantidad', 1)
            CarritoProducto.objects.create(carrito=carrito, producto=producto, cantidad=cantidad)
        
        return carrito

    def update(self, instance, validated_data):
        productos_data = validated_data.pop('carritoproducto_set', [])
        
        # Actualizar los campos básicos del carrito
        instance.usuario = validated_data.get('usuario', instance.usuario)
        instance.save()

        # Actualizar productos
        for producto_data in productos_data:
            producto = producto_data.get('producto')
            cantidad = producto_data.get('cantidad', 1)

            carrito_producto, created = CarritoProducto.objects.get_or_create(carrito=instance, producto=producto)
            if not created:
                carrito_producto.cantidad = cantidad
            carrito_producto.save()
        
        return instance

# Serializador de Pedido
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'


