from django.db import models
from django.contrib.auth.models import User


class OrderStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class Address(models.Model):
    user = models.PositiveIntegerField()
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.street}, {self.city}"

class Order(models.Model):
    product = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)  # Relación con Address
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.product}"
    

class Orden(models.Model):
    cliente_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total de la orden
    status = models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('ENVIADO', 'Enviado'),('ENTREGADO', 'Entregado')], default='PENDIENTE')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)  # Relación con Address
    pago = models.ForeignKey('payments.Pago', on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes')


    def __str__(self):
        return f"Orden #{self.id} - Usuario: {self.usuario.username}"
    
class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="detalles")  # Relación con la orden
    producto_id = models.PositiveIntegerField()  # ID del producto
    nombre = models.CharField(max_length=255)  # Nombre del producto
    cantidad = models.PositiveIntegerField()  # Cantidad de productos
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio unitario del producto
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Descuento en porcentaje (ejemplo: 10 = 10%)
    precio_con_descuento = models.DecimalField(max_digits=10, decimal_places=2)  # Precio final después del descuento

    def __str__(self):
        return f"{self.cantidad} x {self.nombre} (Orden #{self.orden.id})"


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial de {self.order} - {self.status.name}"


class Route(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="route")
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    estimated_time = models.IntegerField()
    distance = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Route for Order {self.order.id}"
    
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)  # Asegúrate de que este campo esté presente
    estado = models.CharField(max_length=100)  # Asegúrate de que este campo esté presente
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre
    

