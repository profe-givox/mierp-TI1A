from django.db import models
from django.contrib.auth.models import User



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
    Username = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
    foto = models.ImageField(upload_to='fotos_empleados/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.Username_id:
            user = User.objects.create_user(
                username=self.correo.split('@')[0],
                email=self.correo,
                password=self.rfc,
                first_name=self.nombre,
                last_name=self.apellidos
            )
            self.Username = user
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellidos} - {self.puesto}'


    
class Nomina(models.Model):
    codigo = models.CharField(primary_key=True, max_length=6)
    folioEmpleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nomina_folioEmpleado')
    nombre = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nomina_nombre')
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    fecha_pago = models.DateField("Fecha de pago")
    salario_diario = models.DecimalField("Salario diario", max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    dias_trabajados = models.IntegerField()  # Máximo depende de la aplicación
    dias_pagados = models.IntegerField()  # Máximo depende de la aplicación
    fecha_inicial = models.DateField("Fecha de inicio")
    fecha_final = models.DateField("Fecha final")
    TIPO_NOMINA = [
        ('S', 'Semanal'),
        ('Q', 'Quincenal'),
        ('M', 'Mensual'),
        ('A', 'Anual'),
        ('AG', 'Aguinaldo'),
        ('O', 'Ordinario'),
        ('F', 'Finiquito')
    ]
    tiponomina = models.CharField(max_length=2, choices=TIPO_NOMINA)  # Se ajusta a 2 ya que algunos valores tienen más de un carácter
    descontar_ahorro = models.BooleanField()
    monto_DA = models.DecimalField(max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    descontar_prestamo = models.BooleanField()
    monto_DP = models.DecimalField(max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    total_percepciones = models.DecimalField(max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    deducciones = models.DecimalField(max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    subtotal = models.DecimalField("Subtotal", max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales
    salario_final = models.DecimalField("Total", max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales

class Percepciones(models.Model):
    codigo = models.CharField(primary_key=True, max_length=3)
    nombre = models.CharField(max_length=100)  # Se agregó el atributo max_length
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Máximo 10 dígitos en total, 2 decimales

class Salida_Entrada(models.Model):
    codigo_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)  # Relación con Empleado
    hora = models.DateTimeField(auto_now_add=True)
    ENTRADA_SALIDA = [
        ('E', 'Entrada'),
        ('S', 'Salida')
    ]
    opcion = models.CharField(max_length=1, choices=ENTRADA_SALIDA)



