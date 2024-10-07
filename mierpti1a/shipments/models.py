# shipments/models.py
from django.db import models

# Definición del modelo Order
class Order(models.Model):
    product = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=100)
    delivery_address = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Pending')
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.product}"

# Definición del modelo Route usando 'Order' como referencia
class Route(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='route')
    starting_point = models.CharField(max_length=255, help_text="Dirección de inicio")
    destination = models.CharField(max_length=255, help_text="Dirección de destino")
    estimated_time = models.IntegerField(help_text="Tiempo estimado en minutos", null=True, blank=True)
    distance = models.FloatField(help_text="Distancia en kilómetros", null=True, blank=True)

    def __str__(self):
        return f"Ruta para Pedido #{self.order.id}"
