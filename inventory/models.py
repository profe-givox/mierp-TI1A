import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MovimientoInventario(models.Model):
    """
    Modelo para registrar entradas y salidas de inventario, incluyendo referencia al pedido.
    """
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    producto_id = models.IntegerField()  # Referencia al ID del producto desde POS
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    sucursal_id = models.IntegerField()  # Referencia al ID de la sucursal desde POS
    pedido = models.ForeignKey(
        'Pedido', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Referencia al pedido que originó este movimiento, si aplica."
    )

    def __str__(self):
        return f"{self.tipo.title()} - Producto ID {self.producto_id} - Cantidad {self.cantidad}"


class Pedido(models.Model):
    """
    Modelo para gestionar pedidos de productos.
    """
    ESTADO_PEDIDO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
    ]

    producto_id = models.IntegerField()  # Referencia al ID del producto desde POS
    cantidad = models.PositiveIntegerField()
    proveedor = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_PEDIDO_CHOICES, default='pendiente')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)  # Se llenará al marcar como entregado

    def __str__(self):
        return f"Pedido {self.id} - Producto ID {self.producto_id} - Estado {self.estado}"



class RegistroAnalisis(models.Model):
    """
    Modelo para registrar informes y análisis generados.
    """
    tipo_informe = models.CharField(max_length=50)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    detalle = models.JSONField()  # Guardar detalles como datos JSON (e.g., resultados de análisis)

    def __str__(self):
        return f"Informe {self.tipo_informe} generado el {self.fecha_generacion}"


class StockEnPedido(models.Model):
    """
    Modelo para registrar productos actualmente en pedido y su cantidad.
    """
    producto_id = models.IntegerField()  # Referencia al ID del producto desde POS
    cantidad_en_pedido = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        Sobrescribir el método save para eliminar el registro solo si ya existe en la base de datos
        y `cantidad_en_pedido` es 0.
        """
        if self.pk and self.cantidad_en_pedido == 0:  # Verifica si el objeto ya existe en la BD
            super().delete(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Producto ID {self.producto_id} - En Pedido: {self.cantidad_en_pedido}"


