from django.db import models

# Create your models here.

class Payment(models.Model):
    name = models.CharField(max_length=200)

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    rfc = models.CharField(max_length=13)

    def __str__(self):
        return self.nombrez
    

class Pago(models.Model):
    TIPO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta', 'Tarjeta'),
        ('PayPal', 'PayPal'),
        ('Vale', 'Vale'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.nombre}"

class Efectivo(models.Model):
    metodo_pago = models.OneToOneField(Pago, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

class Tarjeta(models.Model):
    metodo_pago = models.OneToOneField(Pago, on_delete=models.CASCADE)
    no_tarjeta = models.CharField(max_length=16)
    fecha_vencimiento = models.CharField(max_length=7)
    cvv = models.CharField(max_length=4)

class PayPal(models.Model):
    metodo_pago = models.OneToOneField(Pago, on_delete=models.CASCADE)
    email = models.EmailField()
    estado_de_cuenta = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('suspendida', 'Suspendida'),
        ('cerrada', 'Cerrada'),
    ])

class Vale(models.Model):
    metodo_pago = models.OneToOneField(Pago, on_delete=models.CASCADE)
    numero_vale = models.CharField(max_length=255)
    

class FacturaPorCobrar(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Vencida', 'Vencida'),
        ('Pagada', 'Pagada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    importe = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Factura {self.id} - {self.cliente.nombre}"
    

class GestionDisputaDePagos(models.Model):
    ESTADO_CHOICES = [
        ('En proceso', 'En proceso'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto_disputado = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Disputa {self.id} - {self.cliente.nombre}"
    

    