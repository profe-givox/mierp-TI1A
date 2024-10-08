# Generated by Django 4.2.11 on 2024-10-01 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empleados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idempleado', models.CharField(max_length=1000)),
                ('nombre', models.CharField(max_length=50)),
                ('usuario', models.CharField(max_length=50)),
                ('contrasenia', models.CharField(max_length=16)),
                ('telefono', models.CharField(max_length=15)),
                ('caja', models.IntegerField()),
                ('rol', models.CharField(choices=[('ADM', 'Administrador'), ('EMP', 'Empleado'), ('GER', 'Gerente'), ('SUP', 'Supervisor')], default='EMP', max_length=3)),
                ('idsucursal', models.CharField(choices=[('URI', 'Uriangato'), ('PURU', 'Puruandiro'), ('YURI', 'Yuriria')], default='URI', max_length=5)),
            ],
        ),
    ]
