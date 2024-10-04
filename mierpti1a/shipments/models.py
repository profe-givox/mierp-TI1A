# shipments/models.py
from django.db import models

class Order(models.Model):
    product = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=100)
    delivery_address = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Pending')
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.product}"
