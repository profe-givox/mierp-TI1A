from django.db import models

class Pago(models.Model):
    TIPO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('PayPal', 'PayPal'),
        ('Vale', 'Vale'),
    ]

    cliente_id = models.PositiveIntegerField()  # ID del cliente (relación lógica, no FK)
    tipo = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - Cliente ID: {self.cliente_id} - Monto: {self.monto}"

# Modelos relacionados con una relación de 1 a 1
class DetalleTarjeta(models.Model):
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='detalle_tarjeta')
    nombre_titular = models.CharField(max_length=255)
    no_tarjeta = models.CharField(max_length=16)
    fecha_vencimiento = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4)

class DetallePayPal(models.Model):
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='detalle_paypal')
    nombre_titular = models.CharField(max_length=255) 
    email = models.EmailField()

class DetalleVale(models.Model):
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='detalle_vale')
    numero_vale = models.CharField(max_length=255)
