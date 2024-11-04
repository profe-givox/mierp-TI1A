from django.db import models

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre} - {self.sucursal}'


class Puesto(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre} - {self.departamento}'


class Empleado(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'),
        ('C', 'Casado/a'),
        ('D', 'Divorciado/a'),
        ('V', 'Viudo/a'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero = models.CharField(max_length=15)
    fecha_nac = models.DateField("Fecha de nacimiento")
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES)
    edad = models.IntegerField()
    correo = models.EmailField(max_length=254)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    rfc = models.CharField(max_length=13)
    curp = models.CharField(max_length=18)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    folioEmpleado = models.CharField(max_length=5)
    contraseña = models.CharField(max_length=8)
    foto = models.ImageField(upload_to='fotos_empleados/', null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellidos} - {self.puesto}'
