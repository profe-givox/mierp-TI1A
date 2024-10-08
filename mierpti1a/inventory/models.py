from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class EmpleadoManager(BaseUserManager):
    def crear_empleado(self, email, nombre_usuario, password=None, **extra_fields):
        if not email:
            raise ValueError('El empleado debe tener un correo electrónico')
        empleado = self.model(
            email=self.normalize_email(email),
            nombre_usuario=nombre_usuario,
            **extra_fields
        )
        empleado.set_password(password)
        empleado.save(using=self._db)
        return empleado

    def crear_superusuario(self, email, nombre_usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.crear_empleado(email, nombre_usuario, password, **extra_fields)

class Empleado(AbstractBaseUser):
    nombre_usuario = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    puesto = models.CharField(max_length=100)
    fecha_contratacion = models.DateField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = EmpleadoManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellidos']

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'

    @property
    def es_staff(self):
        return self.is_admin


class Producto(models.Model):
    nombre_producto = models.CharField(max_length=255)
    proveedor = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    cantidad_por_unidad = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades_en_existencia = models.IntegerField()
    unidades_en_pedido = models.IntegerField()
    nivel_reorden = models.IntegerField()  # ReorderLevel

    def __str__(self):
        return self.nombre_producto


class Almacen(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class UbicacionProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    estante = models.CharField(max_length=50)
    lugar = models.CharField(max_length=50)  # Por ejemplo, un número de caja o posición en el estante
    cantidad = models.IntegerField()

    def __str__(self):
        return f'{self.producto.nombre_producto} en estante {self.estante}, lugar {self.lugar}'

    def agregar_stock(self, cantidad):
        """Incrementar el stock en tiempo real"""
        self.cantidad += cantidad
        self.save()

    def retirar_stock(self, cantidad):
        """Disminuir el stock en tiempo real"""
        if self.cantidad >= cantidad:
            self.cantidad -= cantidad
            self.save()
        else:
            raise ValueError('No hay suficiente stock para retirar')


class Orden(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_orden = models.DateField()
    fecha_envio = models.DateField()
    direccion_envio = models.CharField(max_length=255)

    def __str__(self):
        return f'Orden {self.id}'


class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.orden} - {self.producto}'

    def procesar_detalle(self):
        """Procesar la salida del stock para cada producto"""
        ubicacion_producto = UbicacionProducto.objects.get(producto=self.producto)
        ubicacion_producto.retirar_stock(self.cantidad)
