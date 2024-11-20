from rest_framework import serializers
from .models import Producto, Carrito, Pedido, CarritoProducto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'imagen', 'descuento']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True}  # Hacer que la imagen no sea obligatoria y permitir nulo
        }

    def update(self, instance, validated_data):
        # Si 'imagen' no está en los datos validados, se conserva la imagen existente
        if 'imagen' not in validated_data:
            validated_data['imagen'] = instance.imagen

        # Manejar otros campos, si existen
        return super().update(instance, validated_data)

class CarritoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoProducto
        fields = ['id', 'carrito', 'producto', 'cantidad']

class CarritoSerializer(serializers.ModelSerializer):
    productos = CarritoProductoSerializer(many=True, source='carritoproducto_set')

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'productos']

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'carrito', 'total', 'direccion_envio', 'fecha_pedido', 'estado']
