# Generated by Django 5.1.2 on 2024-11-09 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0002_alter_producto_options_producto_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='descripcion',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producto_id', models.IntegerField()),
                ('nombre', models.CharField(max_length=255)),
                ('cantidad', models.IntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='pos.venta')),
            ],
        ),
    ]
