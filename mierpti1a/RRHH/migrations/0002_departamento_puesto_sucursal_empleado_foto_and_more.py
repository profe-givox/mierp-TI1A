# Generated by Django 4.2.16 on 2024-10-07 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("RRHH", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Departamento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Puesto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Sucursal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("direccion", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="empleado",
            name="foto",
            field=models.ImageField(
                blank=True, null=True, upload_to="fotos_empleados/"
            ),
        ),
        migrations.AddField(
            model_name="empleado",
            name="sucursal",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="RRHH.sucursal",
            ),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="departamento",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="RRHH.departamento",
            ),
        ),
        migrations.AlterField(
            model_name="empleado",
            name="puesto",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="RRHH.puesto",
            ),
        ),
    ]
