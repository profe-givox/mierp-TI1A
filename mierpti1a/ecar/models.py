from django.db import models
from django.contrib.auth.models import User

# Modelo de Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Carrito
class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='CarritoProducto')

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

# Modelo de relación entre Carrito y Producto (Cantidad)
class CarritoProducto(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

# Modelo de Pedido
class Pedido(models.Model):
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.CharField(max_length=255)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    ESTADO_PEDIDO = (
        ('P', 'Procesando'),
        ('E', 'Enviado'),
        ('L', 'Entregado'),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_PEDIDO, default='P')

    def __str__(self):
        return f"Pedido {self.id} - Estado: {self.get_estado_display()}"

